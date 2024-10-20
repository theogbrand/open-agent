from simbian.taskgen.agent import Agent
from simbian.taskgen.wrapper import ConversationWrapper

def llm(system_prompt: str, user_prompt: str) -> str:
    ''' Here, we use OpenAI for illustration, you can change it to your own LLM '''
    # ensure your LLM imports are all within this function
    from openai import OpenAI
    
    # define your own LLM here
    client = OpenAI()
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        temperature = 0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# Verify that llm function is working
# print(llm(system_prompt = 'You are a classifier to classify the sentiment of a sentence', 
#     user_prompt = 'It is a hot and sunny day'))

# exit()

# Create a basic agent
basic_agent = Agent(
    agent_name="BasicBot",
    agent_description="A simple bot that greets users",
    llm = llm
)

# Create a conversation wrapper
conv_agent = ConversationWrapper(
    agent=basic_agent,
    persistent_memory={"user_name": "The name of the user"},
    person="User"
)

# Initial state of shared_variables
print("Initial shared_variables:", conv_agent.shared_variables)

# Simulate a conversation
try:
    while True:
        print("shared_variables:", conv_agent.shared_variables)
        user_input = input('User: ')
        if user_input == 'exit': break
        reply = conv_agent.chat(user_input)
        print("shared_variables:", conv_agent.shared_variables)
        print(conv_agent.agent_name + ':', reply)
        print()
except TypeError as e:
    print(f"TypeError occurred: {e}")