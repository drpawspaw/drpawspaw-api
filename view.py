import gradio as gr
from linker.ned import entity_linker

examples = [
    ["My dog has been vomiting and has diarrhea"],
    ["My dog has been vomiting has Limb Swelling and has diarrhea"]
]

def predict_disease(text):
    return ", ".join([e[0] for e in entity_linker(text)])

app = gr.Interface(
    fn=predict_disease,
    inputs=gr.inputs.Textbox(lines=5, label="Input Text"),
    outputs=gr.outputs.Textbox(label="Generated Text"),
    examples=examples
)

app.launch(share=True)