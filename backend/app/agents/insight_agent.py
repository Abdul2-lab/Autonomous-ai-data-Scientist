"""
Agent 10 -- Insight Generation Agent.
Builds insights strictly from already-computed numbers. If an LLM is
configured, it is used only to phrase the grounded facts more naturally --
it is explicitly instructed never to introduce new figures. Without an LLM
key, a deterministic template-based summary is produced instead (clearly
labeled as such), so the feature still works end to end.
"""
from app.llm.llm_factory import get_llm_provider


class InsightAgent:
    name = "insight_agent"

    SYSTEM_PROMPT = (
        "You are a data-science assistant. You will be given ALREADY-COMPUTED facts "
        "about a dataset and ML experiment. Rephrase them clearly and concisely for a "
        "business reader. Do NOT invent, estimate, or alter any numbers. Do NOT claim "
        "things not present in the provided facts. If asked something the facts don't "
        "cover, say so explicitly."
    )

    def run(self, profiling: dict, quality_findings: list, eda_findings: list,
            ml_results: dict | None, explainability: dict | None) -> dict:

        key_findings = list(eda_findings)
        limitations = []
        next_steps = []

        missing_total = sum(profiling.get("missing_values", {}).values())
        if missing_total > 0:
            worst_col = max(profiling.get("missing_values", {}), key=profiling.get("missing_values", {}).get)
            key_findings.insert(0, f"Dataset contains {missing_total} missing values in total; column "
                                    f"'{worst_col}' is the most affected.")

        if profiling.get("duplicate_rows", 0) > 0:
            key_findings.append(f"{profiling['duplicate_rows']} duplicate row(s) were detected and removed during cleaning.")

        model_summary = None
        clustering = (ml_results or {}).get("clustering")
        if clustering is not None:
            if clustering.get("available"):
                sil = clustering.get("silhouette")
                sizes = ", ".join(f"cluster {c['cluster']}: {c['size']} rows" for c in clustering["clusters"])
                key_findings.append(
                    f"Unsupervised clustering (KMeans) found {clustering['best_k']} groups "
                    f"(silhouette={sil:.3f}); sizes: {sizes}."
                )
                top = clustering.get("distinguishing_features", [])[:3]
                if top:
                    key_findings.append("Features that differ most between clusters: " +
                                        ", ".join(d["feature"] for d in top) + ".")
                if sil is not None and sil < 0.25:
                    limitations.append("Silhouette is low, so the clusters overlap and may not be meaningful groups.")
                next_steps.append("Review the cluster profiles and check whether they map to real business segments.")
                next_steps.append("Select a target column and re-run if you want a predictive model instead of clustering.")
            else:
                limitations.append(clustering.get("reason", "Clustering could not be performed."))
        elif ml_results and ml_results.get("best_model_name"):
            best_name = ml_results["best_model_name"]
            best_exp = next((e for e in ml_results.get("experiments", []) if e.get("model_name") == best_name), None)
            if best_exp:
                metric_name = best_exp["metrics"].get("primary_metric")
                metric_value = best_exp["metrics"].get(metric_name)
                model_summary = f"Best performing model: {best_name} ({metric_name}={metric_value})."
                key_findings.append(model_summary)
            next_steps.append("Validate the selected model on new, unseen data before production use.")
        elif clustering is None:
            limitations.append("No machine learning model could be reliably trained on this dataset.")

        if explainability and explainability.get("available"):
            top = explainability["top_features"][:3]
            if top:
                names = ", ".join(f["feature"] for f in top)
                key_findings.append(f"Most influential features: {names}.")
        elif explainability:
            limitations.append(explainability.get("reason", "Feature importance was not available."))

        if profiling.get("high_cardinality_columns"):
            limitations.append(f"High-cardinality columns detected: {profiling['high_cardinality_columns']}; "
                                "these may need special encoding or exclusion.")

        if not next_steps:
            next_steps.append("Collect more data or additional features to improve analysis depth.")
        next_steps.append("Review flagged outliers and data-quality warnings before making business decisions.")

        rule_based = {
            "key_findings": key_findings,
            "limitations": limitations if limitations else ["No major limitations identified from the available data."],
            "next_steps": next_steps,
            "generated_by": "rule_based",
        }

        provider = None
        try:
            provider = get_llm_provider()
        except Exception:
            provider = None

        if provider is None:
            rule_based["llm_note"] = (
                "AI-narrated insights are unavailable because no LLM API key is configured. "
                "The findings above were generated directly from the computed analysis."
            )
            return rule_based

        try:
            facts_block = "\n".join(f"- {f}" for f in key_findings)
            prompt = (
                f"Computed facts:\n{facts_block}\n\n"
                f"Limitations:\n" + "\n".join(f"- {l}" for l in rule_based['limitations']) + "\n\n"
                "Write a short, plain-language executive summary (4-6 sentences) using ONLY these facts."
            )
            narrative = provider.generate(prompt, system=self.SYSTEM_PROMPT)
            rule_based["executive_summary"] = narrative
            rule_based["generated_by"] = "llm_grounded"
        except Exception as e:
            rule_based["llm_note"] = f"LLM narrative generation failed, falling back to computed findings only: {e}"

        return rule_based
