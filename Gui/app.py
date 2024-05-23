import webview

webview.create_window('Comms', 'GUI/aresUI/index.html', maximized=True, js_api=True)
webview.start()