import dotenv
from openai import OpenAI
import openai
import functools
import os

dotenv.load_dotenv()

def handle_openai_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except openai.RateLimitError as e:
            raise Exception("Rate limit exceeded. Please wait a few seconds before trying again.") from e
        except openai.APITimeoutError as e:
            raise Exception("Request timed out. Please try again later.") from e
        except openai.InternalServerError as e:
            raise Exception("Internal server error. Please try again later.") from e
        except openai.APIConnectionError as e:
            raise Exception("API connection error. Please try again later.") from e
        except openai.AuthenticationError as e:
            raise Exception("Authentication error. Please check your API key.") from e
        except openai.OpenAIError as e:
            raise Exception("An error occurred. Please try again later.") from e
    return wrapper


class OpenAIClient:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        default_headers={"OpenAI-Beta": "assistants=v2"}
    )

    @staticmethod
    def chat_assistant(assistant_id):
        """
        retrieves the chat assistant.

        Args:
            assistant_id: The assistant ID.

        Returns:
            dict: The assistant object.
        """
        return OpenAIClient.client.beta.assistants.retrieve(assistant_id)

    @staticmethod
    @handle_openai_errors
    def create_thread(content):
        """
        Creates a thread.

        Args:
            content: The initial message content.

        Returns:
            dict: The thread object.
        """
        return OpenAIClient.client.beta.threads.create(
            messages=[{"role": "user", "content": str(content)}],
        )

    @staticmethod
    def retrieve_thread(thread_id):
        """
        Retrieves a thread.

        Args:
            str: The thread ID.

        Returns:
            dict: The thread object.
        """
        if thread_id.startswith("thread_"):
            return OpenAIClient.client.beta.threads.retrieve(thread_id)

    @staticmethod
    def delete_thread(thread_id):
        """
        Deletes a thread.

        Args:
            str: The thread ID.

        Returns:
            None
        """
        if thread_id.startswith("thread_"):
            OpenAIClient.client.beta.threads.delete(thread_id)

    @staticmethod
    @handle_openai_errors
    def create_message(thread, msg):
        """
        Creates a message in a thread.

        Args:
            thread: The thread object.
            msg: The message content.

        Returns:
            str: The status of the message.
        """
        return OpenAIClient.client.beta.threads.messages.create(
            thread.id,
            role="user",
            content=msg,
        )

    @staticmethod
    @handle_openai_errors
    def create_run(assistant, thread):
        """
        Creates a run for an assistant in a thread.

        Args:
            assistant: The assistant object.
            thread: The thread object.

        Returns:
            str: The status of the run.
        """
        return OpenAIClient.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

    @staticmethod
    def check_run(thread, run):
        """
        Checks the status of a run.

        Args:
            thread: The thread object.
            run: The run object.
        
        Returns:
            str: The status of the run.
        """
        return OpenAIClient.client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        ).status

    @staticmethod
    def get_last_msg(run):
        """
        Retrieves the last message in a thread.

        Args:
            run: The run object.

        Returns:
            str: The content of the last message in the thread.
        """
        return OpenAIClient.client.beta.threads.messages.list(
            thread_id=run.thread_id,
        ).data[0].content[0].text.value

    @staticmethod
    def get_thread_messages(thread):
        """
        Retrieves all messages in a thread.

        Args:
            thread: The thread object.

        Returns: 
            list: A list of messages in the thread.
        """
        messages = OpenAIClient.client.beta.threads.messages.list(thread_id=thread.id)
        messages_data = [m for m in messages.data]
        return messages_data
    
    @staticmethod
    def cancel_run(thread, run):
        """
        Cancels a run.

        Args:
            thread: The thread object.
            run: The run object.

        Returns:
            str: The status of the run after cancellation.
        """
        return OpenAIClient.client.beta.threads.runs.cancel(thread_id=thread.id, run_id=run.id).status
    
    @staticmethod
    def delete_message(thread, message):
        """
        Deletes a message from a thread.

        Args:
            thread: The thread object.
            message: The message object.
        
        Returns:
            bool: True if the message was deleted successfully, False otherwise.
        """
        message = OpenAIClient.client.beta.threads.messages.delete(thread_id=thread.id, message_id=message.id)
        return message.deleted
    
    @staticmethod
    def delete_last_msg_with_response(thread):
        """
        Deletes the last message and response in a thread.

        Args:
            thread: The thread object.

        Returns:
            bool: True if the last message and response were deleted successfully, False otherwise.
        """
        messages = OpenAIClient.get_thread_messages(thread)
        return OpenAIClient.delete_message(thread, messages[0]) and OpenAIClient.delete_message(thread, messages[1])
    
    @staticmethod
    def get_token_usage(thread):
        """
        Retrieves the token usage for an assistant in a thread.

        Args:
            assistant: The assistant object.
            thread: The thread object.

        Returns:
            int: The total number of tokens used of last run.
        """
        return OpenAIClient.client.beta.threads.runs.list(
            thread_id=thread.id,
        ).data[0].usage.total_tokens