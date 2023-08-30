# Customer Service ChatBot

The bot uses the GPT 3.5 language model to function. Its role is to handle various user questions using its specialized functions. Additionally, Langchain provides a facilitated environment for interacting with the LLM.

The standout feature of the customer chatbot is no dependency on user dataset for fine tuning. In fact, many small to mid size businesses do not have their own customer care dataset. Plus, using a dataset of a larger company with related services is not always a beneficial choice due to specific client requirements of each business.
As an alternative solution we are using function calling and prompt engineering that are considered easier options while enhancing the chatbot's service quality. These attributes offer a more advantageous solution for creating a customized chatbot to meet specific requirements. 

Moreover, by using Python data structures, a conversational memory has been built for the bot to respond to the current prompt based on past conversations, resulting in an improved chatting experience. The bot's memory size is configurable, making it more convenient for developers and users with varying levels of infrastructure to work with the app.

V6: In this version, clickable tiles are also added to the bot where they make the user able to submit access request form by having a chat (verbally ask the bot) or, as a faster solution, just click on icons.
