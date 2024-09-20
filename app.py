import gradio as gr
import edge_tts
import asyncio
import os
from rvc_python.infer import RVCInference

#config
output_folder = "outputs"
output_filename = "output.wav"
rvc_folder = "rvc_models"
rvc_filename = "converted.wav"
#init
allVoices = []
voiceChoices = []
rvci = RVCInference()
rvcmodels = rvci.list_models()
rvcmodels.sort()
use_oldver = False;

async def init():
    def simplify(name,gender):
        simplename = name.split(" - ")
        return simplename[1] + " - " + simplename[0].split(" ")[1] + " ["+ gender +"]"
    for v in (await (edge_tts.list_voices())):
        allVoices.append({"label":simplify(v["FriendlyName"],v["Gender"]),"value":v["ShortName"],"locale":v["Locale"],"gender":v["Gender"]})
    for voice in allVoices:
        voiceChoices.append(voice["label"])
    voiceChoices.sort()

def updateRVCModels():
    rvci.models = rvci._load_available_models()
    models = rvci.list_models()
    models.sort()
    return gr.Dropdown(choices=models)


def getVoiceInfo(voices):
    return next((x["value"] for x in allVoices if x["label"] == voices), allVoices[0]["value"])

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
    return audio_file

def rvcSwitch(model,old_ver):
    global use_oldver
    if rvci.current_model!=None:
        if rvci.current_model!=model or use_oldver!=old_ver:
            rvci.unload_model()
            rvci.load_model(model,"v1" if old_ver==True else "v2")
            use_oldver=old_ver
    else:
        rvci.load_model(model,"v1" if old_ver==True else "v2")
        use_oldver=old_ver

def rvcInfer(active, inp, model, old_ver, pitch):
    if active==False:
        return None
    if model==None:
        return None
    rvcSwitch(model,old_ver)
    rvci.set_params(f0up_key=pitch)
    rvc_out = os.path.join(os.path.join(os.path.dirname(__file__), output_folder, rvc_filename))
    return rvci.infer_file(inp, rvc_out)

async def ui():
    with gr.Blocks(title="Simple Edge-TTS + RVC") as webui:
        gr.Markdown("""# Simple Text to Speech using Edge-TTS + RVC
                ### Speech is generated with Edge-TTS first, then converted to another character's voice with RVC""")
        with gr.Row():
            with gr.Column():
                text = gr.TextArea(label="Text Here", info="The text that will be spoken")
                btn = gr.Button("Generate")
                clr = gr.Button("Clear")
            with gr.Column():
                with gr.Accordion("TTS Option"):
                    voices = gr.Dropdown(choices=voiceChoices,
                                value=voiceChoices[0] if len(voiceChoices)>0 else None,
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
                                label="Volume",
                                info="Increase or decrease volume",
                                interactive=True)
                    gr.Markdown("You can also upload your own audio file below to convert with RVC")
                    audio = gr.Audio(label="TTS Output",
                                type="filepath",
                                show_download_button=True,
                                interactive=True)
                    tts_btn = gr.Button("Generate Speech")
                    tts_btn.click(fn=textToSpeech,
                            inputs=[text, voices, rate, volume],
                            outputs=[audio])
                with gr.Accordion("RVC Voice Changer",open=False):
                    rvc_on = gr.Checkbox(value=False,
                                label="RVC Active",
                                info="Convert TTS output with RVC")
                    rvc_voice = gr.Dropdown(choices=rvcmodels,
                                value=rvcmodels[0] if len(rvcmodels)>0 else None,
                                label="Voice",
                                info="Select RVC voice")
                    old_ver = gr.Checkbox(value=False,
                                label="Model is v1",
                                info="Check this if model is v1")
                    rvc_pitch = gr.Slider(-24,
                                24,
                                step=1,
                                value=0,
                                label="Pitch",
                                info="Change pitch from input (+higher, -lower)")
                    rvc_refresh = gr.Button("Refresh Models")
                    rvc_refresh.click(fn=updateRVCModels,
                                    outputs=rvc_voice)
                    audio_convert = gr.Audio(label="RVC Converted",
                                type="filepath",
                                interactive=False)
                    rvc_btn = gr.Button("Convert with RVC")
                    rvc_btn.click(fn=rvcInfer,
                            inputs=[rvc_on, audio, rvc_voice, old_ver, rvc_pitch],
                            outputs=[audio_convert])
                btn.click(fn=textToSpeech,
                        inputs=[text, voices, rate, volume],
                        outputs=[audio]).then(fn=rvcInfer,
                                            inputs=[rvc_on, audio, rvc_voice, old_ver, rvc_pitch],
                                            outputs=[audio_convert])
                clr.click(lambda: [None,None,None],
                        outputs=[text,audio,audio_convert])
    webui.queue()
    webui.launch()

if __name__ == "__main__":
    asyncio.run(init())
    asyncio.run(ui())
