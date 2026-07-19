from assistants import Assistant, Orchestrator, handoff, RunContextWrapper
from assistants.extensions import handoff_filters
from assistants.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pydantic import BaseModel
import asyncio

# Define structured input for escalation handoff
class EscalationData(BaseModel):
    reason: str
    priority: str
    customer_id: str

# Create specialized assistants
escalation_agent = Assistant(
    name="Escalation Assistant",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You handle escalated customer issues. You have access to additional tools and authority
    to resolve complex problems that first-level support cannot handle.
    """
)

# Callback function for escalation tracking
async def on_escalation_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    """Callback executed when escalation handoff is triggered"""
    print(f"🚨 ESCALATION ALERT:")
    print(f"   Reason: {input_data.reason}")
    print(f"   Priority: {input_data.priority}")
    print(f"   Customer ID: {input_data.customer_id}")

# Create advanced handoff with custom configuration
escalation_handoff = handoff(
    assistant=escalation_agent,
    tool_name_override="escalate_to_manager",
    tool_description_override="Escalate complex issues that require manager intervention",
    on_handoff=on_escalation_handoff,
    input_type=EscalationData  # Structured input required
)

# Advanced triage assistant
root_agent = Assistant(
    name="Advanced Triage Assistant",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are an advanced customer service assistant with escalation capabilities.
    
    Handle most issues yourself, but use escalations for:
    - Angry customers or complex complaints
    - Issues requiring refunds > $100
    - Technical problems you cannot resolve
    
    When escalating, provide reason, priority (low/medium/high), and customer_id.
    """,
    handoffs=[escalation_handoff]
)

# Example usage
async def main():
    print("⚡ OpenAI Agents SDK - Advanced Handoffs")
    print("=" * 50)
    
    # Test escalation with structured input
    print("=== Escalation with Structured Input ===")
    result = await Orchestrator.run(
        root_agent,
        """I am absolutely furious! Your service has been down for 3 days and I've lost thousands 
        of dollars in business. I want a full refund of my annual subscription ($299) and 
        compensation for my losses. My customer ID is CUST-789123."""
    )
    print(f"Response: {result.final_output}")
    
    print("\n✅ Advanced handoffs tutorial complete!")

if __name__ == "__main__":
    asyncio.run(main())
