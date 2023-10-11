from llm import LLM
import streamlit as st

# streamlit run main.py

def main():
    st.title("Bookie")

    if "llm" not in st.session_state:
        st.session_state.llm = LLM()

    if "processing" not in st.session_state:
        st.session_state.processing = False

    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state.processing:
        if prompt := st.chat_input("Say something"):
            st.session_state.processing = True

            if prompt == "reset":
                st.session_state.llm.reset_memory()
                st.session_state.processing = False
            else:
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("ai"):
                    with st.empty():
                        response = st.session_state.llm.chat(prompt)
                        st.session_state.messages.append({"role": "ai", "content": response})
                        st.session_state.processing = False

if __name__ == '__main__':
    main()