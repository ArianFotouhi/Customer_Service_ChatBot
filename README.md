# Customer Service ChatBot

The bot uses the GPT 3.5 language model to function. Its role is to handle various user questions using its specialized functions. Additionally, Langchain provides a facilitated environment for interacting with the LLM.

The standout feature of the app is its ability to call functions, enhancing the chatbot's service quality. This attribute offers a simpler solution for creating a customized chatbot to meet specific requirements. It eliminates the need to generate personal datasets and train the model on them to achieve fine-tuning.

Moreover, by using Python data structures, a conversational memory has been built for the bot to respond to the current prompt based on past conversations, resulting in an improved chatting experience. The bot's memory size is configurable, making it more convenient for developers and users with varying levels of infrastructure to work with the app.

V5: despite previous versions, this version uses the language model once within one request submission process. In this way when a form is shown to be created, the bot will reply a constant string (previously it used to rephrase and make a new response each time). The benefit of this solution is less credit usage. 
