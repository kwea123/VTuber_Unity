# VTuber_Unity
Use Unity 3D character and Python deep learning algorithms to stream as a VTuber!

Youtube Playlist (Chinese):
[![teaser](images/teaser.jpg)](https://www.youtube.com/playlist?list=PLDV2CyUo4q-JFGrpG595jMdWZLwYOnu4p)

--------------------------------------------------------------------------------
# Credits
First of all, I'd like to give credits to the following projects that I borrow code from:
1.  [head-pose-estimation](https://github.com/yinguobing/head-pose-estimation) [LICENSE](licenses/LICENSE.head-pose-estimation)
2.  [face-alignment](https://github.com/1adrianb/face-alignment) [LICENSE](licenses/LICENSE.face-alignment)

And the virtual character [unity-chan](http://unity-chan.com/) © UTJ/UCL.

# Installation

## Hardware
*  OS: Ubuntu 16.04 (Windows support is under testing)
*  An NVIDIA GPU with CUDA>=9.0 (CPU support is under testing)

## Software
*  Unity 
   *  [linux installation](https://forum.unity.com/threads/unity-on-linux-release-notes-and-known-issues.350256/)
   *  [Windows installation](https://unity3d.com/get-unity/download)
*  Python3.6 (may be compatible with other versions)
   * Install the requirements by `pip install -r requirements.txt`.
*  Optional
   * [OBS Studio](https://obsproject.com/) if you want to embed the virtual character into your videos.
   
# Example usage
1.  Execute `unity.x86_64` to launch the unity window featuring the virtual character (unity-chan here).
2.  After the vitual character shows up, run `python demo.py --cam 0 --connect` to synchronize your face features with the virtual character.

# Functionalities
In this section, I will describe the functionalities implemented and a little about the technology behind.

## Head pose estimation
Using [credit 1](https://github.com/yinguobing/head-pose-estimation) and [credit 2](https://github.com/1adrianb/face-alignment) ,deep learning methods are applied to do the following: face detection and facial landmark detection. A face bounding box and the 68-point facial landmark is detected, then I use a PnP algorithm to obtain the head pose (the rotation of the face). Finally, kalman filters are applied to the angles to make them smoother.

## Miscellaneous

Estimate [eye aspect ratio](https://www.google.com/search?q=eye+aspect+ratio&rlz=1C1GCEU_jaJP829JP829&oq=eye&aqs=chrome.0.69i59j69i57j69i65j69i61.846j0j7&sourceid=chrome&ie=UTF-8), [mouth aspect ratio](https://www.google.com/search?rlz=1C1GCEU_jaJP829JP829&sxsrf=ACYBGNR1ME-HV3c5avZ15yahkkQd1omjpw%3A1571114646809&ei=lk6lXcyIMZ-Rr7wP0OCX8A4&q=mouth+aspect+ratio&oq=mouth+aspect+ratio&gs_l=psy-ab.3..35i39j0i203.30193.31394..31535...0.0..0.109.710.4j3......0....1..gws-wiz.......0i7i30j0i8i30j0i10i30j0i7i10i30j0i8i7i30j0i13j0i13i30j0i13i5i30.IWlXGoyW5GE&ved=0ahUKEwjMq7KTup3lAhWfyIsBHVDwBe4Q4dUDCAs&uact=5), etc.

# License
[MIT License](LICENSE)
