import gradio as gr
import edge_tts
import asyncio
import os

#config
output_folder = "outputs"
output_filename = "output.mp3"
#init
allVoices = []
voiceChoices = []
async def init():
    def simplify(name):
        simplename = name.split(" - ")
        return simplename[1] + " - " + simplename[0].split(" ")[1]
    for v in (await (edge_tts.list_voices())):
        allVoices.append({"label":simplify(v["FriendlyName"]),"value":v["ShortName"],"locale":v["Locale"],"gender":v["Gender"]})
    for voice in allVoices:
        voiceChoices.append(voice["label"])
    voiceChoices.sort()

def getVoiceInfo(voices):
    return next((x["value"] for x in allVoices if x["label"] == voices), "id-ID-GadisNeural")

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

async def ui():
    with gr.Blocks(title="Simple Edge-TTS") as webui:
        gr.Markdown("""# Simple Text to Speech using Edge-TTS library""")
        with gr.Row():
            with gr.Column():
                text = gr.TextArea(label="Text Here", info="The text that will be spoken" , elem_classes="text-area")
                btn = gr.Button("Generate", elem_id="submit-btn")
            with gr.Column():
                voices = gr.Dropdown(choices=voiceChoices,
                                    value="Indonesian (Indonesia) - Gadis",
                                    label="Speakers",
                                    info="Select language / speaker",
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
    webui.launch()

if __name__ == "__main__":
    asyncio.run(init())
    asyncio.run(ui())