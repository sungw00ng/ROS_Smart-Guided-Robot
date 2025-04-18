src/pyaudio/device_api.c:9:10: fatal error: 'portaudio.h' file not found<br>
      #include "portaudio.h"<br>
               ^~~~~~~~~~~~~<br>
      1 error generated.<br>
      error: command '/usr/bin/gcc' failed with exit code 1<br>
      [end of output]<br>
  <br>
  note: This error originates from a subprocess, and is likely not a problem with pip.<br>
  ERROR: Failed building wheel for pyaudio<br>
Failed to build pyaudio<br>
ERROR: Could not build wheels for pyaudio, which is required to install pyproject.toml-based projects<br>

[해결 방법]
https://www.youtube.com/watch?v=GD6wxUOLXn4<br>
homebrew 설치 후, 터미널에서<br>
brew install portaudio<br>
pip install pyaudio <br>
입력하면 해결완료:)<br>
