import streamlit as st
from openai_api import OpenAIAPI

openai_api = OpenAIAPI()

num_questions = st.number_input("Number of questions", min_value=1, max_value=10)

files = st.file_uploader("Upload files", accept_multiple_files=True)

def create_container_with_color(id, color="#E4F2EC"):
    # todo: instead of color you can send in any css
    plh = st.container()
    html_code = """<div id = 'my_div_outer'></div>"""
    st.markdown(html_code, unsafe_allow_html=True)

   
    with plh:
        inner_html_code = """<div id = 'my_div_inner_%s'></div>""" % id
        plh.markdown(inner_html_code, unsafe_allow_html=True)

    ## applying style
    chat_plh_style = """
        <style>
            div[data-testid='stVerticalBlock']:has(div#my_div_inner_%s):not(:has(div#my_div_outer)) {
                background-color: %s;
                border-style: solid;
                border-width: 1px;
                border-color: black;
                padding: 10px;
                width: 110%%;
                align-items: center;
                align-self: center;
            };
        </style>
        """
    chat_plh_style = chat_plh_style % (id, color)

    st.markdown(chat_plh_style, unsafe_allow_html=True)
    return plh

def button_click(id, value):
    st.session_state[f"{id}"]["user_answer"] = value

def radio_change(id):
    if f"{id}_choice" not in st.session_state:
        return
    
    value = st.session_state[f"{id}_choice"]

    if value == st.session_state[f"{id}"]["choice1"]:
        st.session_state[f"{id}"]["user_answer"] = "choice1"
    elif value == st.session_state[f"{id}"]["choice2"]:
        st.session_state[f"{id}"]["user_answer"] = "choice2"
    elif value == st.session_state[f"{id}"]["choice3"]:
        st.session_state[f"{id}"]["user_answer"] = "choice3"
    elif value == st.session_state[f"{id}"]["choice4"]:
        st.session_state[f"{id}"]["user_answer"] = "choice4"

def build_true_or_false_ui(question, answer, user_answer, id):
    if user_answer == None:
        color = "#00000000"
    elif user_answer != answer:
        color = "#EE4B2B"
    else:
        color = "#00ff00"
    with create_container_with_color(id=id, color=color):
        q = st.write(f"Question: {question}")
        button_true = st.button("True", key=f"{id}_true", on_click=button_click, args=(id, "true"))
        button_false = st.button("False", key=f"{id}_false", on_click=button_click, args=(id, "false"))

def build_multiple_choice_ui(question, choice1, choice2, choice3, choice4, answer, user_answer, id):
    if user_answer == None:
        color = "#00000000"
    elif user_answer != answer:
        color = "#EE4B2B"
    else:
        color = "#00ff00"

    with create_container_with_color(id=id, color=color):
        q = st.radio(f"Question: {question}",
                     options=[choice1,
                              choice2,
                              choice3,
                              choice4],
                     key=f"{id}_choice",
                     on_change=radio_change,
                     args=(id,),
                     index=["choice1", "choice2", "choice3", "choice4"].index(st.session_state[f"{id}"]["user_answer"]) if st.session_state[f"{id}"]["user_answer"] != None else None)

if files != [] and "q0" not in st.session_state:
    print("files != [] and q0 not in st.session_state")
    file_paths = [file.name for file in files]
    try:
        print("Creating quiz...")
        tool_outputs = openai_api.create_quiz(num_questions=num_questions, files=files)
    except:
        print("There was an error creating the quiz. Retrying...")
        st.error("There was an error creating the quiz. Retrying...")
        st.rerun()

    i = 0
    for tool_output in tool_outputs:
        print(f"Adding tool output {i}")
        st.session_state[f"q{i}"] = tool_output["output"]
        st.session_state[f"q{i}"]["user_answer"] = None
        i += 1

for q in sorted(st.session_state.keys()):
    if "q" not in q: continue
    if "choice" in q: continue
    if "_true" in q: continue
    if "_false" in q: continue

    print(q)
    if st.session_state[q]["question_type"] == "true_or_false":
        question = st.session_state[q]["question"]
        answer = st.session_state[q]["answer"]
        id = q
        print(f"Building true or false UI for {id}")
        print(f"User answer: {st.session_state[q]['user_answer']}")
        build_true_or_false_ui(question=question, answer=answer, user_answer=st.session_state[q]["user_answer"], id=id)
    elif st.session_state[q]["question_type"] == "multiple_choice":
        question = st.session_state[q]["question"]
        choice1 = st.session_state[q]["choice1"]
        choice2 = st.session_state[q]["choice2"]
        choice3 = st.session_state[q]["choice3"]
        choice4 = st.session_state[q]["choice4"]
        answer = st.session_state[q]["answer"]
        id = q
        print(f"Building multiple choice UI for {id}")
        print(f"User answer: {st.session_state[q]['user_answer']}")
        build_multiple_choice_ui(question=question, choice1=choice1, choice2=choice2, choice3=choice3, choice4=choice4, answer=answer, user_answer=st.session_state[q]["user_answer"], id=id)