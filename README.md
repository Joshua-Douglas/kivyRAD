# KivyRad
KivyRAD is intended to speed up the kivy widget development process by introducing widget and application hot-reloading. Components are reloaded by restarting the visualized widget or application in a separate process. In the future, we hope to support a property editor that is capable of applying changes without a complete restart. 

The application is in the alpha phase, and currenly only supports windows development. Feature suggestions and contributions are welcome. 

# Application Setup
This project uses `venv` for dependency management. A powershell script, `build_env.ps1`, is provided to build the virtual environment, and clean the `requirements.txt` file. 

Once the virtual environment you can launch the application by simply running `main.py`:

```
python main.py
```

To begin visualizing, open your kivy project select the widget from the auto-populated list of widgets, or select the file to visualize. Edits to the selected widget will be shown in realtime, in a separate kivy window. 

![modalmsg_hotreload](https://user-images.githubusercontent.com/22138019/216899557-c8117325-372f-416a-b3fb-6514ede7d780.gif)
