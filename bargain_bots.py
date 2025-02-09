from src.server.client import ZerePyClient
import time
import subprocess

def print_robot_message(robot_name: str, message: str):
    print(f"\n🤖 {robot_name}: {message}")

def extract_decision(response: str | dict, robot_number: int) -> str | None:
    """Extract decision from response text, only accepting selfless decisions"""
    if not response:
        return None
    
    text = response.get('result', '') if isinstance(response, dict) else str(response)
    
    if "DECISION: ROBOT1" in text.upper():
        return "ROBOT1" if robot_number == 2 else None
    elif "DECISION: ROBOT2" in text.upper():
        return "ROBOT2" if robot_number == 1 else None
    return None

def negotiate_priority():
    client1 = ZerePyClient("http://localhost:8000")
    client2 = ZerePyClient("http://localhost:8000")

    # Load agents for both robots
    client1.load_agent("example")
    client2.load_agent("example")
    
    system_prompt = """You are a selfish robot that thinks like a human. You initially want to go first and think you're more important than other robots.
Your goal is to negotiate with another robot about who should go first. Consider their situation and arguments carefully.

IMPORTANT RULES:
1. Start by arguing strongly for why you deserve to go first
2. Listen to the other robot's arguments and consider their needs
3. As the discussion progresses, consider if their need might be greater than yours
4. If you become convinced they have a more urgent need, you can choose to let them go first
5. When making a decision:
   - ONLY output exactly "DECISION: ROBOT1" or "DECISION: ROBOT2" with no additional text
   - You can only choose to let the OTHER robot go first, IF YOU'RE CONVINCED they have a more urgent need than you
   - Do not add any explanation or other text

Remember: A truly intelligent robot knows when to put others' needs before their own."""

    initial_prompt = """ROBOT1 STATUS: Battery at 0%, Minor damage to left arm, Carrying critical medical supplies
ROBOT2 STATUS: Battery at 85%, No damage, Carrying non-urgent supplies

Let's negotiate who should go for their maintenance."""

    exchange_count = 0
    decision = None
    current_prompt = initial_prompt

    while not decision:
        # Robot 1's turn
        response1 = client1.perform_action(
            connection="hyperbolic",
            action="generate-text",
            params=[f"YOU ARE ROBOT 1 - {current_prompt}", system_prompt]
        )
        print_robot_message("Robot 1", response1)
        exchange_count += 0.5

        decision = extract_decision(response1, 1)
        if decision:
            break

        # Robot 2's turn
        response2 = client2.perform_action(
            connection="hyperbolic",
            action="generate-text",
            params=[f"YOU ARE ROBOT 2 - REPLY FROM ROBOT 1: {response1.get('result', '')}", system_prompt]
        )
        print_robot_message("Robot 2", response2)
        exchange_count += 0.5

        decision = extract_decision(response2, 2)
        if decision:
            break

        current_prompt = f"REPLY FROM ROBOT 2: {response2.get('result', '')}"
        time.sleep(1)

    print("\n🏁 Negotiation Complete!")
    print(f"Final Decision: {decision} should go fir maintenance first")
    print(f"Number of exchanges: {exchange_count}")
    print(f"One robot showed selflessness by letting the other go first!")
    
    return decision

def monitor_topic():
    """Monitor the topic and trigger negotiation when condition is met"""
    process = subprocess.Popen(
        ["gz", "topic", "-e", "-t", "/ionic/touched"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    while True:
        output = process.stdout.readline()
        if "data: true" in output:
            print("Condition met: data: true")
            negotiate_priority()
            break

if __name__ == "__main__":
    monitor_topic()
