# History
## 0.0.3 (2023-07-13)
- **VimeoShocase** und **VimeoFolder**: property **nb_videos**
- **VimeoData** changed property names
	- video_count -> nb_videos
	- showcases_count -> nb_showcases
	- folders_count -> nb_folders

## 0.0.2 (2023-07-12)
- VimeoData gets the methods **save** and **load**, to save or load data as json or pickle. 
- the **__init__** of VimeoVideo, VimeoShowcase, VimeoFolder gets a parameter **data**, where the data can be passed when the object is created, so no request is needed.
- Objects have a new attribute **temp_data** (dictionary) where you can store data relevant to your runing program directly on the object.
- The **VimeoData** object can be added to **VimeoVideo**, **VimeoShowcase** and **VimeoFolder** instances. So the data object can be updated if there is a change in one of those instances.
- using **pathlib** (instead of os.path): all filepath parameters accept Path objects.

Still no unit tests, this is still very much in beta!

## 0.0.1 (2023-07-07)
This is the first version. It provides the **VimeoConnection**, **VimeoData**, **Video** and **VimeoShowcase** and **VimeoFolder** classes.

The package is still very much in beta, as many of the possible methods of this classes are not implemented yet and other classes (e.g. for Groups or Portfolios) shall be implemented later. It is also not well tested at the moment. Use it at your own risk!
