import gradio as gr
import edge_tts
import asyncio
import os

#config
output_folder = "outputs"
output_filename = "output.mp3"
#init
allVoices = []
voiceChoices = ["Microsoft Gadis Online (Natural) - Indonesian (Indonesia)"]
async def init():
    for v in (await (edge_tts.list_voices())):
        allVoices.append({"label":v["FriendlyName"],"value":v["ShortName"],"locale":v["Locale"],"gender":v["Gender"]})
    for voice in allVoices:
        voiceChoices.append(voice["label"])

def getVoiceInfo(voices):
    return "id-ID-GadisNeural"
    #find voice in allVoices list
    #print(next((i for i, x in enumerate(allVoices) if [x==voices]), ["id-ID-GadisNeural"]))
    #return voices

async def textToSpeech(text, voices, rate, volume):
    voices = getVoiceInfo(voices)
    if (rate >= 0):
        rates = rate = "+" + str(rate) + "%"
    else:
        rates = str(rate) + "%"
    if (volume >= 0):
        volumes = "+" + str(volume) + "%"
    else:
        volumes = str(volume) + "%"
    communicate = edge_tts.Communicate(text,
                                       voices,
                                       rate=rates,
                                       volume=volumes,
                                       proxy=None)
    audio_file = os.path.join(os.path.dirname(__file__), output_folder, output_filename)
    await communicate.save(audio_file)
    if (os.path.exists(audio_file)):
        return audio_file
    else:
        raise gr.Error("File not found!")

def clearSpeech():
    output_file = os.path.join(os.path.dirname(__file__), output_folder, output_filename)
    if (os.path.exists(output_file)):
        os.remove(output_file)
    return None, None

with gr.Blocks(title="Simple Edge-TTS") as demo:
    gr.Markdown("""# Simple Text to Speech using Edge-TTS library""")
    with gr.Row():
        with gr.Column():
            text = gr.TextArea(label="Text Here", elem_classes="text-area")
            btn = gr.Button("Generate", elem_id="submit-btn")
        with gr.Column():
            voices = gr.Dropdown(choices=voiceChoices,
                                value="Microsoft Gadis Online (Natural) - Indonesian (Indonesia)",
                                label="Speakers",
                                info="Select speaker",
                                interactive=True)
            rate = gr.Slider(-100,
                            100,
                            step=1,
                            value=0,
                            label="Speech Speed",
                            info="Speek faster or slower",
                            interactive=True)
            volume = gr.Slider(-100,
                            100,
                            step=1,
                            value=0,
                            label="Pitch",
                            info="Increase or decrease pitch",
                            interactive=True)
            audio = gr.Audio(label="Output",
                            interactive=False,
                            elem_classes="audio")
            clear = gr.Button("Clear", elem_id="clear-btn")
            btn.click(fn=textToSpeech,
                    inputs=[text, voices, rate, volume],
                    outputs=[audio])
            clear.click(fn=clearSpeech, outputs=[text, audio])

asyncio.run(init())

if __name__ == "__main__":
    demo.launch()