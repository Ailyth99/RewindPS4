package main

import (
	"embed"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
	"github.com/wailsapp/wails/v2/pkg/options/windows"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	// Create an instance of the app structure
	app := NewApp()
	psn := &PSN{}
	px := &Proxy{}

	px.CheckClientActivity()

	// Create application with options
	err := wails.Run(&options.App{
		Title:  "RewindPS4",
		Width:  1030,
		Height: 790,

		//Frameless:                true, // HIDE DEFAULT TITLE BAR

		DisableResize:            true, //MAIN WINDOW RESIZE
		Fullscreen:               false,
		EnableDefaultContextMenu: true,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		BackgroundColour: &options.RGBA{R: 59, G: 52, B: 69, A: 1}, //cancel default background color
		//window options
		Windows: &windows.Options{
			WebviewIsTransparent:              true,
			WindowIsTranslucent:               false,
			DisableWindowIcon:                 false,
			DisableFramelessWindowDecorations: false,
			WebviewUserDataPath:               "",
			Theme:                             windows.Dark, //https://wails.io/docs/reference/options/#theme
			CustomTheme: &windows.ThemeSettings{
				DarkModeTitleBar:   windows.RGB(11, 11, 11),
				DarkModeTitleText:  windows.RGB(255, 255, 222), //TEXT COLOR
				DarkModeBorder:     windows.RGB(20, 0, 20),
				LightModeTitleBar:  windows.RGB(10, 15, 26),
				LightModeTitleText: windows.RGB(255, 255, 222),
				LightModeBorder:    windows.RGB(10, 15, 26),
			},
		},

		//bind golang src（app, psn, px)to frontend
		OnStartup: app.startup,
		Bind: []interface{}{
			app,
			psn,
			px,
		},
	})

	if err != nil {
		println("Error:", err.Error())
	}
}
