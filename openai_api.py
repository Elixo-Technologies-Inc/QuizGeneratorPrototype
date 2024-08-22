from dotenv import load_dotenv
from openai import OpenAI
import os
import time
import json
import yaml

load_dotenv()

class OpenAIAPI():
    def __init__(self):
        self.client = OpenAI()
        self.functions = self.load_functions(folder_path="./functions")
        
    def create_quiz(self, num_questions, files):
        messages = [
            {
                "role": "user", 
                "content": f"Create {num_questions} questions for a quiz, balancing the type of questions.",
            },
        ]
        
        vector_store = self.upload_files(files)
        assistant = self.create_assistant(vector_store=vector_store, functions=self.functions)
        thread = self.create_thread(messages=messages)
        run = self.create_run(thread_id=thread.id, assistant_id=assistant.id)
        tool_outputs = self.get_tool_outputs(run=run)
        return tool_outputs

    def create_assistant(self, vector_store, functions):
        assistant = self.client.beta.assistants.create(name="assistant_quiz", 
                                          instructions="You are a private tutor who provides practice exams and quizzes for students who want to study for their classes.  Read from the provided material and build questions based on the material.  Use the language used in the material.",
                                          model="gpt-4o-mini", 
                                          tools=[{"type": "file_search"},
                                                 {"type": "function",
                                                  "function": functions["create_true_or_false"]},
                                                 {"type": "function",
                                                  "function": functions["create_multiple_choice"]}],
                                          tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
                                        )
        return assistant

    def create_thread(self, messages):
        thread = self.client.beta.threads.create(
            messages=messages
        )
        return thread

    def create_run(self, thread_id, assistant_id):
        run = self.client.beta.threads.runs.create_and_poll(thread_id=thread_id,
                                                           assistant_id=assistant_id)
        return run

    def get_messages(self, thread_id):
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages

    def get_tool_outputs(self, run):
        # Define the list to store tool outputs
        tool_outputs = []
         
        # Loop through each tool in the required action section
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            tool_outputs.append({
              "tool_call_id": tool.id,
              "output": json.loads(tool.function.arguments)
            })
         
        return tool_outputs
    
    def upload_files(self, files):
        message_files = files
        vector_store = self.client.beta.vector_stores.create(name="temp_vstore")
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
          vector_store_id=vector_store.id, files=message_files
        )
        while file_batch.status == "processing":
            print("Processing file batch...")
            time.sleep(1)
        return vector_store

    def load_functions(self, folder_path):
        # Dictionary to hold all the loaded .yml files
        loaded_files = {}
        
        # Iterate over all .yml files in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".yml"):
                file_path = os.path.join(folder_path, filename)
                # Load the .yml file content into a dictionary
                with open(file_path, 'r') as file:
                    file_content = yaml.safe_load(file)
                
                # Get the name for the dictionary (file name without extension)
                dict_name = os.path.splitext(filename)[0]
                
                # Assign the content to the dictionary with the corresponding name
                loaded_files[dict_name] = file_content
        return loaded_files