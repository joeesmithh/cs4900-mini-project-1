# CS 4900 Mini Project 1

## Camera Application for Visually Impaired Individuals

### Deadlines

- September 15: Project demo day

### Background

- When we think of cameras and photography, we falsely believe that only visually able individuals should be able to take photographs. In HCI we talk about making interfaces that are accessible to all users.
- Companies have recognized this issue and released tools for visually impaired users, for example Google released Guided Frame that uses voice commands and haptic feedback to help visually impaired users take photos.

### Task

- You will create a desktop applications that enable visually impaired users to take images of an object of interest using only speech-based commands.
- The applications can be created using any programming language.

### Workflow

- The display should be divided into 4 quadrants and a center section, hereby named top-left, top-right, bottom-left, bottom-right, and center.
- The user will specify the position where they want their object using commands such as: "top left", "top right", "bottom left", "bottom right", and "center". The commands will be provided as speech inputs only.
- Your application should guide the user to take an image of the scene using the camera on their computer.
- Your application will then detect the objects in the scene using
any off-the-shelf object detector.
  - Hint: you can control what objects you want in the scene, so pick objects that are easily detected by the detector.
- Your application will ask the user what object they want to image and where they want the object. The locations would be top-left, top-right, bottom-left, bottom-right, and center.
- Your application must then guide the user to move their computer and/or camera so they can image the desired object and place it in their chosen location.
- Your application must check for what percentage of the object is in the desired location before taking the image.

### Helpful Links

- [Object Detection](https://huggingface.co/facebook/detr-resnet-50)
- [Text2Speech](https://huggingface.co/tasks/text-to-speech)