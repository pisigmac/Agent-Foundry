import streamlit as st
import asyncio
from assistant import iterate_spec_until_acceptance

st.set_page_config(page_title="Loop Assistant Demo", page_icon=":repeat:", layout="wide")

st.title("🔁 Iterative Plan Refiner with Gemini 3 Flash(Loop Assistant)")
st.markdown(
    """
This demo runs a LoopAgent that repeatedly executes sub-assistants to iteratively refine a plan.

Loop characteristics:
- Executes its sub-assistants sequentially in a loop
- Terminates when the session's `accepted` flag is set or after the target iterations
- Shares the same session state across iterations, so counters/flags persist
    """
)

account_id = "demo_loop_user"

st.header("Run an iterative refinement")
topic = st.text_area(
    "Topic",
    value="AI-powered customer support platform launch plan",
    height=100,
    placeholder="What plan/topic should be refined iteratively?",
)

col_a, col_b = st.columns([1, 1])
with col_a:
    target_iterations = st.number_input(
        "Target iterations (early stop possible)", min_value=1, max_value=20, value=3, step=1
    )
with col_b:
    st.caption(
        "Set a reasonable number of iterations. The loop may stop earlier if the session state flag `accepted` becomes True."
    )

if st.button("Run Loop Refinement", type="primary"):
    if topic.strip():
        st.info("Refining plan in a loop…")
        with st.spinner("Working…"):
            try:
                results = asyncio.run(
                    iterate_spec_until_acceptance(account_id, topic, int(target_iterations))
                )
                st.success("Loop finished")

                st.subheader("Final Refined Plan")
                st.write(results.get("final_plan", ""))

                st.subheader("Run Metadata")
                st.write({
                    "iterations": results.get("iterations"),
                    "stopped_reason": results.get("stopped_reason"),
                })
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("Please enter a topic")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        - Uses `LoopAgent` with 3 sub-assistants:
          1) `plan_refiner` (LLM) refines the plan
          2) `increment_iteration` updates the iteration counter in session state
          3) `check_completion` escalates when done (accepted flag or target reached)
        - The same `InvocationContext` and session state are reused every iteration
        - The loop stops if `accepted` is True or the `target_iterations` is reached.
        """
    )

