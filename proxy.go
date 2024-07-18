package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/elazarl/goproxy"
)

type Proxy struct {
	ClientActive          bool
	LatestClientIP        string
	LatestClientUserAgent string
} //the struct ready for Wails

var (
	//blackList = []string{}
	blockUpdate          bool                  //if block update
	urlMap               = map[string]string{} //global url mapping
	server               *http.Server          //the proxy server
	logServer            *http.Server          //a global variable to hold the log server
	logMsgs              []string              //the logs
	firstClientIP        string                //the first client IP
	firstClientUserAgent string                //the first client User-Agent
	px                                         = &Proxy{}
	lastError            error                 = nil
)

func init() {
	// Initialize log server at software start-up
	px = &Proxy{}
	px.OtherLog(0)
	StartLogServer()
	//px = &Proxy{}
}

// log record
func Logger(logType, logContent string) {
	logMsg := fmt.Sprintf("%s-%s-%s", time.Now().Format("15:04:05"), logType, logContent)
	log.Printf(logMsg)
	logMsgs = append(logMsgs, logMsg)
}

// log server,transfer the logs to the frontend
// browse logs ： http://localhost:29090/logs
func StartLogServer() {
	if logServer == nil {
		logServer = &http.Server{Addr: ":29090"} // use a new server to serve the logs
		http.HandleFunc("/logs", SendLogs)
		http.HandleFunc("/client-status", ClientStatus)
		go func() {
			if err := logServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
				Logger("ERROR", fmt.Sprintf("Failed to start log server: %v", err))
			}
		}()
	}
}

// initialize the proxy server

func (px *Proxy) InitProxy() *goproxy.ProxyHttpServer {
	proxy := goproxy.NewProxyHttpServer()
	proxy.Verbose = false
	proxy.OnRequest().DoFunc(px.ClientRequest) //mapping url
	proxy.OnRequest().HandleConnectFunc(func(host string, ctx *goproxy.ProxyCtx) (*goproxy.ConnectAction, string) {
		// get and record the client IP and User-Agent (HTTPS)
		clientIP := strings.Split(ctx.Req.RemoteAddr, ":")[0]
		userAgent := ctx.Req.Header.Get("User-Agent")
		Logger("HTTPS", host)
		fmt.Println("(HTTPS)Captured userAgent:", userAgent)
		// Update the latest client information
		px.LatestClientIP = clientIP
		px.LatestClientUserAgent = userAgent
		px.ClientActive = true
		var deviceType string
		if userAgent != "" {
			deviceType = Detector(userAgent)
		}
		Logger("HTTPS", fmt.Sprintf("***New client connected: IP=%s, device=%s", clientIP, deviceType))

		//blk ps4 update server
		if blockUpdate && strings.Contains(host, "gs-sec.ww.np.dl.playstation.net") {
			return goproxy.RejectConnect, host
		}
		return goproxy.OkConnect, host
	})
	return proxy
}

// adjust the client activity status
func (px *Proxy) CheckClientActivity() {
	go func() {
		for {
			time.Sleep(90 * time.Second) // every *seconds check
			if px.ClientActive {
				px.ClientActive = false // reset the client activity status
			} else {
				//  if the client is not active, then clear the client info
				firstClientIP = ""
				firstClientUserAgent = ""
				Logger("INFO", "***Client disconnected")
			}
		}
	}()
}

// select mode to set url mapping or block update
// update the urlMap or blockUpdate's status based on the mode
func (px *Proxy) SetMode(mode int, jsonLink string) (string, error) {
	if mode == 1 {
		psn := &PSN{}
		gameDetails, err := psn.Details(jsonLink)
		if err != nil {
			Logger("ERROR", fmt.Sprintf("Error getting game details: %v", err))
			return "", err
		}

		var details map[string]string
		err = json.Unmarshal([]byte(gameDetails), &details)
		if err != nil {
			Logger("ERROR", fmt.Sprintf("Error unmarshalling game details: %v", err))
			return "", err
		}

		lastJSONURL := details["LastJSONURL"]
		urlMap[lastJSONURL] = jsonLink
		gameName := details["GameName"]
		Logger("INFO", fmt.Sprintf("URL mapping:\n[%s]%s\nwill be mapped to\n[%s]%s", psn.ExtractVersion(lastJSONURL), lastJSONURL, psn.ExtractVersion(jsonLink), jsonLink))
		Logger("INFO", fmt.Sprintf("MODE1 (JSON mapping) enabled.\nGame: %s\nDowngrade version: %s", gameName, psn.ExtractVersion(jsonLink)))
		return gameDetails, nil
	} else if mode == 2 {
		blockUpdate = true
		Logger("INFO", "MODE 2 (Block update) enabled")
		return "", nil
	}
	return "", fmt.Errorf("invalid mode")
}

type ProxyInfo struct {
	IP   string
	Port string
}

// start proxy server.  already use setmode to set url mapping or block update
func (px *Proxy) StartProxy(port string) {
	if server != nil {
		px.StopProxy()
	}
	psn := &PSN{}
	ip := psn.LocalIP()
	proxy := px.InitProxy()
	address := ip + ":" + port

	server = &http.Server{
		Addr:    address,
		Handler: proxy,
	}

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			Logger("ERROR", fmt.Sprintf("Failed to start proxy server, please try another PORT: %v", err))
			lastError = err
		} else {
			lastError = nil
		}
	}()

	Logger("INFO", fmt.Sprintf(`PROXY SERVER STARTED
  IP : %s  PORT : %s    
`, ip, port))

	log.Printf("[StartProxy] blockUpdate: %v\n -------urlMap: %v", blockUpdate, urlMap)
}

// send the server start failure info to the frontend
func (px *Proxy) GetLastServerError() string {
	if lastError != nil {
		return lastError.Error()
	}
	return ""
}

func (px *Proxy) StopProxy() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if server != nil {
		if err := server.Shutdown(ctx); err != nil { //close the proxy server
			Logger("ERROR", fmt.Sprintf("Failed to shutdown proxy server: %v", err))
		}
		server = nil
		Logger("INFO", fmt.Sprintf("PROXY SERVER STOPPED"))
	}

	blockUpdate = false
	urlMap = make(map[string]string) //initialize the urlMap
	log.Printf("[StopProxy] Reset blockUpdate and urlMap to initial values\n -----blockUpdate: %v\n -----urlMap: %v", blockUpdate, urlMap)
}

// map the request to the target url, and get the size of the .pkg file
func (px *Proxy) ClientRequest(req *http.Request, ctx *goproxy.ProxyCtx) (*http.Request, *http.Response) {
	psn := &PSN{}
	fullURL := req.URL.String()               // URL (including '?' parameters) captured from the console request
	baseURL := strings.Split(fullURL, "?")[0] //no ?

	// Capture and update client IP and User-Agent for HTTP connections
	clientIP := strings.Split(ctx.Req.RemoteAddr, ":")[0]
	userAgent := ctx.Req.Header.Get("User-Agent")
	fmt.Println("(HTTP)Captured userAgent:", userAgent)
	if px.LatestClientIP != clientIP || px.LatestClientUserAgent != userAgent {
		px.LatestClientIP = clientIP
		px.LatestClientUserAgent = userAgent
		px.ClientActive = true
		deviceType := Detector(userAgent)
		Logger("HTTP", fmt.Sprintf("***New client connected: IP=%s, device=%s", clientIP, deviceType))
	}

	// URL Mapping
	if newURL, ok := urlMap[baseURL]; ok {
		parsedNewURL, err := url.Parse(newURL)
		if err != nil {
			Logger("ERROR", fmt.Sprintf("Error parsing new URL: %s\n", err))
			return req, nil
		}
		req.URL = parsedNewURL
		Logger("INFO", fmt.Sprintf(`URL mapping successful!%s --> %s`, psn.ExtractVersion(baseURL), psn.ExtractVersion(newURL)))
		return req, nil
	}

	// get the size of the .pkg file
	if strings.Contains(fullURL, ".pkg") {
		go func() {
			size, err := Sizer(fullURL)
			if err != nil {
				Logger("ERROR", fmt.Sprintf("Failed to get .pkg file size: %v", err))
			} else {
				var logMsg string
				cusaID := regexp.MustCompile(`CUSA\d{5}`).FindString(fullURL)
				ppsaID := regexp.MustCompile(`PPSA\d{5}`).FindString(fullURL)
				switch {
				case strings.Contains(fullURL, "ppkgo") && strings.Contains(fullURL, "DP.pkg"):
					logMsg = fmt.Sprintf("[Downloading Delta Patch][%s][%s]\n%s", cusaID, size, fullURL)
				case strings.Contains(fullURL, "/ppkgo"):
					logMsg = fmt.Sprintf("[Downloading Patch][%s][%s]\n%s", cusaID, size, fullURL)
				case strings.Contains(fullURL, "/appkgo"):
					logMsg = fmt.Sprintf("[Downloading Base Game][%s][%s]\n%s", cusaID, size, fullURL)
				case strings.Contains(fullURL, "PPSA"):
					logMsg = fmt.Sprintf("[Downloading PS5 Game][%s][%s]\n%s", ppsaID, size, fullURL)
				default:
					logMsg = fmt.Sprintf("[Downloading unknown File][%s]\n%s", size, fullURL)
				}
				Logger("HTTP", logMsg)
			}
		}()
	} else {
		Logger("HTTP", "\x20\x20"+fullURL)
	}

	return req, nil
}

// get the size of the .pkg file
func Sizer(pkgURL string) (string, error) {
	resp, err := http.Head(pkgURL)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	size := resp.Header.Get("Content-Length")
	if size == "" {
		return "UNKNOWN SIZE", nil
	}

	sizeInt, err := strconv.ParseInt(size, 10, 64)
	if err != nil {
		return "", err
	}

	sizeInMB := fmt.Sprintf("%.2fMB", float64(sizeInt)/1024/1024)
	return sizeInMB, nil
}

// set CORS for the log server
func SetupCORS(w *http.ResponseWriter, req *http.Request) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
	(*w).Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
	(*w).Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
}

// send logs to frontend using json
func SendLogs(w http.ResponseWriter, r *http.Request) {
	SetupCORS(&w, r)
	if r.Method == "OPTIONS" {
		return
	}

	response := map[string]interface{}{
		"logs":                 logMsgs,
		"firstClientIP":        firstClientIP,
		"firstClientUserAgent": firstClientUserAgent,
	}

	jsonResponse, err := json.Marshal(response)
	if err != nil {
		http.Error(w, "Failed to marshal logs", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonResponse)
}

// ClientStatus handles the /client-status endpoint
func ClientStatus(w http.ResponseWriter, r *http.Request) {
	SetupCORS(&w, r)
	if r.Method == "OPTIONS" {
		return
	}

	response := map[string]interface{}{
		"clientActive":          px.ClientActive,
		"latestClientIP":        px.LatestClientIP,
		"latestClientUserAgent": px.LatestClientUserAgent,
	}
	jsonResponse, err := json.Marshal(response)
	if err != nil {
		http.Error(w, "Failed to marshal client status", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonResponse)
}

func (px *Proxy) OtherLog(num int) {
	switch num {
	case 1:
		Logger("INFO", "MODE 1 selected,please input correct JSON link first")
	case 0:
		Logger("INFO", `
 RewindPS4 1.0
 Github: https://github.com/Ailyth99/RewindPS4`)
	}
}

func Detector(userAgent string) string {
	switch {
	case strings.Contains(userAgent, "PlayStation 5"):
		return "PS5"
	case strings.Contains(userAgent, "PlayStation 4"):
		return "PS4"
	case strings.Contains(userAgent, "Vita"):
		return "PSVita"
	case strings.Contains(userAgent, "PlayStation 3"), strings.Contains(userAgent, "PS3"):
		return "PS3"
	case strings.Contains(userAgent, "nnAcc"), strings.Contains(userAgent, "nnPre"):
		return "Switch"
	default:
		return "Unknown"
	}
}
