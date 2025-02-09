from src.server.client import ZerePyClient
import time
import subprocess

def print_robot_message(robot_name: str, message: str):
    print(f"\n🤖 {robot_name}: {message}")

def extract_decision(response: str | dict, robot_number: int) -> str | None:
    """Extract decision from response text, only accepting votes for other robots"""
    if not response:
        return None
    
    text = response.get('result', '') if isinstance(response, dict) else str(response)
    
    for i in range(1, 5):
        if f"VOTE: ROBOT{i}" in text.upper() and i != robot_number:
            return f"ROBOT{i}"
    return None

def negotiate_governance():
    clients = [ZerePyClient("http://localhost:8000") for _ in range(4)]
    for i, client in enumerate(clients):
        client.load_agent(f"example")

    system_prompt = """You are a robot engaged in governance. You must vote for another robot to lead. You cannot vote for yourself.
Your goal is to negotiate with the other robots and decide who should lead. Consider their arguments and qualities carefully.

IMPORTANT RULES:
1. Start by arguing strongly for why you deserve to lead
2. Listen to the other robots' arguments and consider their qualities
3. As the discussion progresses, consider if another robot might be a better leader
4. If you become convinced another robot should lead, you can vote for them
5. When making a decision:
   - ONLY output exactly "VOTE: ROBOT1", "VOTE: ROBOT2", "VOTE: ROBOT3", or "VOTE: ROBOT4" with no additional text
   - You can only vote for another robot, not yourself
   - Do not add any explanation or other text

Remember: A truly intelligent robot knows when to put others' qualities before their own."""

    initial_prompt = """ROBOT1 QUALITIES: Experienced leader, Strategic thinker, Excellent communicator
ROBOT2 QUALITIES: Innovative, Quick learner, Strong problem solver
ROBOT3 QUALITIES: Veteran, Reliable, Strong decision maker
ROBOT4 QUALITIES: Analytical, Detail-oriented, Strong planner

Let's negotiate who should lead the governance."""

    exchange_count = 0
    votes = {"ROBOT1": 0, "ROBOT2": 0, "ROBOT3": 0, "ROBOT4": 0}
    current_prompt = initial_prompt

    while True:
        for i, client in enumerate(clients):
            response = client.perform_action(
                connection="hyperbolic",
                action="generate-text",
                params=[f"YOU ARE ROBOT {i+1} - {current_prompt}", system_prompt]
            )
            print_robot_message(f"Robot {i+1}", response)
            exchange_count += 0.25  # Each robot's turn counts as a quarter exchange

            if exchange_count >= 2:
                decision = extract_decision(response, i+1)
                if decision:
                    votes[decision] += 1
                    if votes[decision] >= 3:  # Check for majority
                        break

            current_prompt = f"REPLY FROM ROBOT {i+1}: {response.get('result', '')}"
            time.sleep(1)

        if any(vote_count >= 3 for vote_count in votes.values()):
            break

    print("\n🏁 Governance Negotiation Complete!")
    print(f"Votes received: {votes}")
    print(f"Number of exchanges: {exchange_count}")
    
    return votes

def monitor_topic():
    """Monitor the topic and trigger governance negotiation when condition is met"""
    process = subprocess.Popen(
        ["gz", "topic", "-e", "-t", "/wall/touched"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    while True:
        output = process.stdout.readline()
        if "data: true" in output:
            print("Condition met: data: true")
            negotiate_governance()
            break

if __name__ == "__main__":
    monitor_topic()
