import OpenAIUtils
from FileEditor import FileEditor
from BashCmdExe import BashCommandExecutor
import os
import json
import signal
import sys
from time import sleep

def signal_handler(sig, frame):
    print("\nInterrupted by user. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def process_file_operations(operations):
    for operation in operations:
        editor = FileEditor(data=operation)
        print("processsing file operation")
        return editor.process()

def process_assistant_response(response):
    try:
        data = json.loads(response)
        
        if data['action'] == 'file_operation':
            return process_file_operations(data['action_input']['operations'])
        elif data['action'] == 'bash_command':
            executor = BashCommandExecutor()
            result = executor.execute_commands(json.dumps(data['action_input']))
            print("Bash Command Result:")
            print(result)
            return result
        else:
            print(f"Unknown action: {data['action']}")
        
        return data['task_completed']
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from assistant")
        return False
    except KeyError as e:
        print(f"Error: Missing key in assistant response: {e}")
        return False
    except Exception as e:
        print(f"Error processing assistant response: {e}")
        return False

if __name__ == "__main__":
    task = input("Enter the task: ")

    client = OpenAIUtils.OpenAIClient()
    assistant = client.chat_assistant("asst_w7HCuZmCcwvsdMqPOkl9DRIK")
    print("Assistant initialized.")

    thread = client.create_thread(task)
    print("Thread created ID: ", thread.id)

    task_completed = False
    while not task_completed:
        run = client.create_run(assistant, thread)
        print("Run ID: ", run.id)

        c_t = 0
        while client.check_run(thread, run) != "completed":
            print("Waiting for assistant response...", end='\r')
            sleep(2)
            c_t += 2
            if c_t == 14:
                client.cancel_run(run)

        print("\nRun completed.")

        response = client.get_last_msg(run)
        print("Retrieved response")

        task_completed = process_assistant_response(response)

        if type(task_completed) is str:
            client.create_message(thread, task_completed)
            task_completed = False

        if not task_completed and type(task_completed) is bool:
            user_input = input("Enter your response to continue (exit/continue): ")
            if user_input == "exit":
                break
            elif user_input == "continue":
                pass
            elif user_input:
                client.create_message(thread, user_input)
        
        print("Waiting for 2 seconds...")
        sleep(2)

    print("Task completed successfully.")