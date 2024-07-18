package main

import (
	"crypto/hmac"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/tls"
	"encoding/hex"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net"
	"net/http"
	"os/exec"
	"regexp"
	"runtime"
	"strings"
)

type PSN struct{}

func (ps *PSN) IsValidJSONURL(url string) bool {
	return strings.HasPrefix(url, "http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/") && strings.HasSuffix(url, ".json")
}

func (ps *PSN) PSNXML(CUSA string) string {
	Logger("INFO", "Start check game version")
	keyHex := "AD62E37F905E06BC19593142281C112CEC0E7EC3E97EFDCAEFCDBAAFA6378D84"
	key, _ := hex.DecodeString(keyHex)
	data := []byte("np_" + CUSA)

	h := hmac.New(sha256.New, key)
	h.Write(data)
	hash := hex.EncodeToString(h.Sum(nil))

	xmlURL := fmt.Sprintf("https://gs-sec.ww.np.dl.playstation.net/plo/np/%s/%s/%s-ver.xml", CUSA, hash, CUSA)
	Logger("INFO", fmt.Sprintf("Check version Success: %s", xmlURL))

	//fmt.Println(xmlURL)
	return xmlURL
}

func (ps *PSN) CheckXML(xmlURL string) string {
	// Create a custom HTTP client, disable SSL certificate verification (to open PSN XML links over HTTPS)
	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	// GET request
	resp, err := client.Get(xmlURL)
	if err != nil {
		Logger("ERROR", fmt.Sprintf("Failed to retrieve the latest version from the gs-sec.ww.np.dl.playstation.net: %v\n", err))
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		Logger("ERROR", fmt.Sprintf("PSNXML request failure, error code: %d\n", resp.StatusCode))
		return ""
	}

	// read response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		Logger("ERROR", fmt.Sprintf("Failed to read response body: %v\n", err))
		return ""
	}

	xmlData := string(body)

	return xmlData
}

// XML structure
type TitlePatch struct {
	XMLName xml.Name `xml:"titlepatch"`
	TitleID string   `xml:"titleid,attr"`
	Tag     Tag      `xml:"tag"`
}

type Tag struct {
	Package Package `xml:"package"`
}

type Package struct {
	Version     string   `xml:"version,attr"`
	Paramsfo    Paramsfo `xml:"paramsfo"`
	ManifestURL string   `xml:"manifest_url,attr"`
	ContentID   string   `xml:"content_id,attr"`
}

type Paramsfo struct {
	Title string `xml:"title"`
}

type XMLDetails struct {
	CUSA        string
	GameName    string
	LastVersion string
	LastJSONURL string
	Region      string
}

func (ps *PSN) ExtractXML(xmlData string) (string, error) {
	var titlePatch TitlePatch
	err := xml.Unmarshal([]byte(xmlData), &titlePatch)
	if err != nil {
		return "", fmt.Errorf("error parsing XML: %v", err)
	}
	contentId := titlePatch.Tag.Package.ContentID
	regionCode := contentId[:1]
	var region string
	switch regionCode {
	case "E":
		region = "Europe"
	case "U":
		region = "US"
	case "J":
		region = "Japan"
	case "H":
		region = "Asia"
	case "K":
		region = "Korea"
	case "I":
		region = "Internal"
	default:
		region = "Others"
	}

	details := XMLDetails{
		CUSA:        titlePatch.TitleID,
		GameName:    titlePatch.Tag.Package.Paramsfo.Title,
		LastVersion: titlePatch.Tag.Package.Version,
		LastJSONURL: titlePatch.Tag.Package.ManifestURL,
		Region:      region,
	}
	//to json , to string
	jsonDetails, err := json.Marshal(details)
	if err != nil {
		return "", fmt.Errorf("error marshalling details to JSON: %v", err)
	}

	return string(jsonDetails), nil
}

func (ps *PSN) ExtractVersion(url string) string {
	re := regexp.MustCompile(`-A(\d+)-`)
	match := re.FindStringSubmatch(url)

	if match != nil {
		version := match[1]
		if len(version) > 2 {
			formattedVersion := version[:2] + "." + version[2:]
			return formattedVersion
		}
		return version
	}
	Logger("ERROR", "Failed to retrieve the version, please check if the patch link is correct.")
	return ""
}

func (ps *PSN) ExtractCUSA(url string) string {
	re := regexp.MustCompile(`prod/(CUSA\d+)`)
	match := re.FindStringSubmatch(url)

	if match == nil {
		Logger("ERROR", "Failed to retrieve the CUSA ID, please check if the patch link is correct.")
		return ""
	}
	return match[1]
}

func (ps *PSN) Details(inputJSON string) (string, error) {
	Logger("INFO", "Start retrieve game details")
	CUSA := ps.ExtractCUSA(inputJSON)
	XMLURL := ps.PSNXML(CUSA)
	XMLInfo := ps.CheckXML(XMLURL)

	extractedDetails, err := ps.ExtractXML(XMLInfo)
	if err != nil {
		return "", fmt.Errorf("error parsing XML: %v", err)
	}
	Logger("INFO", "Successfully retrieve game details")
	return extractedDetails, nil
}

func (ps *PSN) Mapper(targetJSON string) (string, error) {
	details, err := ps.Details(targetJSON)
	if err != nil {
		return "", fmt.Errorf("error getting details: %v", err)
	}

	// Parse the 'details' JSON string to retrieve the 'LastJSON' value
	var detailsMap map[string]string
	err = json.Unmarshal([]byte(details), &detailsMap)
	if err != nil {
		return "", fmt.Errorf("error unmarshalling details JSON: %v", err)
	}

	tempJSON := detailsMap["LastJSONURL"]

	mapping := map[string]string{
		"lastJSON":   tempJSON,
		"targetJSON": targetJSON,
	}
	//	process the response as JSON.(convert to string)
	jsonMapping, err := json.Marshal(mapping)
	if err != nil {
		return "", fmt.Errorf("error marshalling mapping to JSON: %v", err)
	}

	return string(jsonMapping), nil
}

func (ps *PSN) TitleMetadataInfo(jsonLink string) (string, error) {
	//Logger("INFO", "Start check game cover")
	cusaID := ps.ExtractCUSA(jsonLink)
	keyHex := "F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0"
	gameID := []byte(cusaID + "_00")
	key, err := hex.DecodeString(keyHex)
	if err != nil {
		return "", fmt.Errorf("hex decode error: %v", err)
	}

	hmacSHA1 := hmac.New(sha1.New, key)
	hmacSHA1.Write(gameID)
	hash := hex.EncodeToString(hmacSHA1.Sum(nil))
	hash = strings.ToUpper(hash)

	tmdbJSONUrl := fmt.Sprintf("http://tmdb.np.dl.playstation.net/tmdb2/%s_00_%s/%s_00.json", cusaID, hash, cusaID)

	response, err := http.Get(tmdbJSONUrl)
	if err != nil {
		return "", fmt.Errorf("http get error: %v", err)
	}
	defer response.Body.Close()

	if response.StatusCode == 404 {
		return "", nil
	} else if response.StatusCode != 200 {
		Logger("ERROR", fmt.Sprintf("Retrieve game cover failed (code: %d)", response.StatusCode))
		return "", fmt.Errorf("tmdb json failed (CODE: %d)", response.StatusCode)
	}

	data, err := io.ReadAll(response.Body)
	if err != nil {
		Logger("ERROR", fmt.Sprintf("read PlayStation tmdb response body error: %v", err))
		return "", fmt.Errorf("read response body error: %v", err)
	}

	var result map[string]interface{}
	err = json.Unmarshal(data, &result)
	if err != nil {
		return "", fmt.Errorf("json unmarshal error: %v", err)
	}

	icons := result["icons"].([]interface{})
	if len(icons) == 0 {
		Logger("INFO", "No game cover found")
		return "", nil
	}
	icon := icons[0].(map[string]interface{})["icon"].(string)

	Logger("INFO", fmt.Sprintf("Successfully retrieve game cover:%s", icon))

	return icon, nil
}

func (ps *PSN) CheckPort(port int) bool {
	addr := fmt.Sprintf("127.0.0.1:%d", port)
	listener, err := net.Listen("tcp", addr)
	if err != nil {
		return true //port used
	}
	listener.Close()
	return false //not used
}

func (ps *PSN) LocalIP() string {
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		Logger("ERROR", fmt.Sprintf("get local IP Error: %v", err))
		return ""
	}
	defer conn.Close()

	localAddr := conn.LocalAddr().(*net.UDPAddr)
	fmt.Println("Your Local IP is:", localAddr.IP.String())
	return localAddr.IP.String()
}

// open system browser
func (ps *PSN) OpenBrowser(url string) error {
	var cmd string
	var args []string

	switch runtime.GOOS {
	case "windows":
		cmd = "cmd"
		args = []string{"/c", "start", url}
	case "darwin":
		cmd = "open"
		args = []string{url}
	default: // "linux", "freebsd", "openbsd", "netbsd"
		cmd = "xdg-open"
		args = []string{url}
	}

	return exec.Command(cmd, args...).Start()
}
