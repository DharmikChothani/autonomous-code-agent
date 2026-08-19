from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from .state import AgentState

from .nodes import (
    planner_node,
    coder_node,
    test_generator_node,
    executor_node,
    tester_node,
    debugger_node,
    reviewer_node,
    critic_node,
    reflection_node,
    final_report_node,
    execution_router,
    critic_router,
)


builder = StateGraph(
    AgentState
)


# -------------------------
# Nodes
# -------------------------

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "coder",
    coder_node
)

builder.add_node(
    "test_generator",
    test_generator_node
)

builder.add_node(
    "executor",
    executor_node
)

builder.add_node(
    "tester",
    tester_node
)

builder.add_node(
    "debugger",
    debugger_node
)

builder.add_node(
    "reviewer",
    reviewer_node
)

builder.add_node(
    "critic",
    critic_node
)

builder.add_node(
    "reflection",
    reflection_node
)

builder.add_node(
    "final_report",
    final_report_node
)


# -------------------------
# Main flow
# -------------------------

builder.add_edge(
    START,
    "planner"
)

builder.add_edge(
    "planner",
    "coder"
)

builder.add_edge(
    "coder",
    "test_generator"
)

builder.add_edge(
    "test_generator",
    "executor"
)

builder.add_edge(
    "executor",
    "tester"
)


# -------------------------
# Tester routing
# -------------------------

builder.add_conditional_edges(
    "tester",
    execution_router,
    {
        "success": "reviewer",
        "debug": "debugger",
        "max_retries": "reviewer",
    },
)


# -------------------------
# Debug loop
# -------------------------

builder.add_edge(
    "debugger",
    "coder"
)


# -------------------------
# Review → Critic
# -------------------------

builder.add_edge(
    "reviewer",
    "critic"
)


# -------------------------
# Critic routing
# -------------------------

builder.add_conditional_edges(
    "critic",
    critic_router,
    {
        "approved":
            "final_report",

        "reflect":
            "reflection",
    },
)


# -------------------------
# Reflection loop
# -------------------------

builder.add_edge(
    "reflection",
    "coder"
)


# -------------------------
# Final
# -------------------------

builder.add_edge(
    "final_report",
    END
)


graph = builder.compile()