# Simple TTS + RVC
A simple text to speech gradio webui using Edge-TTS library,
with voice changing feature using RVC.

## How To Run
> [!NOTE]
> Tested and developed on Python 3.10.  
> This is because [rvc-python](https://github.com/daswer123/rvc-python/issues/27) can only run on Python 3.10 as of now,  
> If you don't want to use RVC, it is fine to use other Python version.
- (Optional but recommended) Make a python 3.10 environment, and activate it:
```
[Windows]
py -3.10 -m venv venv
venv\Scripts\activate

[Linux]
python3.10 -m venv venv
source venv/bin/activate
```
- Install all requirements using:
`pip install -r requirements.txt`
- Then run the gradio with:
`python app.py`
- And visit the url shown in console (default gradio url: http://localhost:7860)

## Library Used
- [Gradio](https://github.com/gradio-app/gradio)
- [Edge-TTS](https://github.com/rany2/edge-tts)
- [rvc-python](https://github.com/daswer123/rvc-python)
- And all dependencies required by these libraries

## RVC Folder Structure
If you want to use RVC function,
put your RVC models in this location:
```
rvc_models/
└── [model_name]/
    ├── [model_name].pth (Required)
    └── [model_name].index (Optional)
```

## Other Notes
- If you are using ARM Linux (aarch64) and can't install rvc-python, 
  most likely because [praat-parselmouth](https://github.com/YannickJadoul/Parselmouth) doesn't have prebuild for aarch64 and failed to build on pip install. 
  Solution: You have to clone praat-parselmouth repo and it's submodules (`git clone --recurse-submodules https://github.com/YannickJadoul/Parselmouth`),  
  then run `pip install` there (in the cloned parselmouth directory).
