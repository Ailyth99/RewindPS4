import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import './locales/i18n';
import baffle from 'baffle';
import './App.css';
import './custom.css';
import {validateJsonInput} from './clutter';
import { LocalIP,CheckPort,OpenBrowser,ExtractVersion,TitleMetadataInfo } from '../wailsjs/go/main/PSN';
import { SetMode, StartProxy, StopProxy,OtherLog,GetLastServerError } from '../wailsjs/go/main/Proxy';
import waitImage from './assets/images/waiting.png';
import noCover from './assets/images/nocover.png';
import kb from './assets/images/kanban.png';
import kinshi from './assets/images/koshinkinshi.png';
import mode0 from './assets/images/mode0.png';
import correctBackground from './assets/images/naiyou2.png';
import incorrectBackground from './assets/images/naiyou.png';

const App: React.FC = () => {
    ///////localization/////////
    const { t } = useTranslation();
    const { i18n } = useTranslation();
    const fontClass = (lang: string) => {
      const languageCode = lang.split('-')[0]; //ignore the region code after "-" ie zh-CN to zh
      switch(languageCode) {
        case 'en':
          return 'font-en';
        case 'zh':
          return 'font-zh';
        case 'ja':
          return 'font-ja';
        default:
          return 'font-en'; 
      }
    };

      //get guide url based on the language
    const getGuideUrl = () => {
      const languageCode = i18n.language.split('-')[0]; 
      if (languageCode === 'zh') {
          return "https://foggy-bath-a54.notion.site/RewindPS4-Guide-1-0-84d3988cce3a4ede8b5cee66a593c371?pvs=4";
      } else {
          return "https://foggy-bath-a54.notion.site/RewindPS4-Guide1-0-ENGLISH-28164b6f656d445f823a0f7c7d9ae890?pvs=4";
      }
    };

  

    ///////alert/////////
    const [showAlert, setShowAlert] = useState(false);
    const [alertMsg, setAlertMsg] = useState('');

    const showAlertWithDelay = () => {
      setTimeout(() => {
        setShowAlert(true);  
      }, 300);  //delay show alert
    };

    const closeAlert = () => {
      setShowAlert(false);
  };

  ///////////////client device/////////////
  const [clientIP, setClientIP] = useState(t('waiting'));
  const [userAgent, setUserAgent] = useState(t('waiting'));
// Fetch client status from the log server
const fetchClientStatus = async () => {
  
  try {
    const response = await fetch('http://localhost:29090/client-status');
    const data = await response.json();
    if (data.clientActive) {
        setClientIP(data.latestClientIP);
        setUserAgent(data.latestClientUserAgent);
    } else {
        //setClientIP(t('waiting'));
        //setUserAgent(t('waiting'));  
    }
  } catch (error) {
    console.error('Failed to fetch client status:', error);
  }
};

useEffect(() => {
  const interval = setInterval(fetchClientStatus, 2000); // 每2秒检查一次
  return () => clearInterval(interval);
}, []);
   

  /////////////mode//////////
    const [mode, setMode] = useState(0);
    const initialGameInfo = {
      gameName: t('waitinginfo'),
      gameId: t('waitinginfo'),
      region: t(''),
      lastVersion: t('waitinginfo'),
      downgradeVersion: t('waitinginfo'),
      imageUrl: waitImage
    };
    const [gameInfo, setGameInfo] = useState(initialGameInfo);
    //port input
    const [serverIp, setServerIp] = useState('localhost');
    const [serverPort, setServerPort] = useState(8080);
          //get ip
          useEffect(() => {
            LocalIP().then(ip => {
              setServerIp(ip);
            }).catch(error => {
              console.error('Failed to fetch local IP:', error);
            });
          }, []);


///////////////////////LOG AREA/////////////////////////////
    const [logs, setLogs] = useState<string[]>([]);
    const logRef = useRef<HTMLDivElement>(null);
    const [filterLogs, setFilterLogs] = useState(false);
    const FilterLogsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFilterLogs(e.target.checked);
    };
    //fetch logs from log server
    // Fetch logs and client info from the log server
    const fetchLogs = async () => {
      try {
          const response = await fetch('http://localhost:29090/logs');
          const data = await response.json();
          if (Array.isArray(data.logs)) {

            let filteredData: string[] = [];
              let latestIP = '';
              let latestUserAgent = '';
  
              data.logs.forEach((log: string) => {
                  // update client info
                  if (log.includes('New client connected')) {
                      const ipMatch = log.match(/IP=([\d\.]+)/);
                      const userAgentMatch = log.match(/device=(.+)/);
                      if (ipMatch && userAgentMatch) {
                          latestIP = ipMatch[1];
                          latestUserAgent = userAgentMatch[1];
                      }
                  }
                  if (log.includes('Client disconnected')) {
                      latestIP = t('waiting');
                      latestUserAgent = t('waiting');
                  }
  
                  // filter logs 
                  if (!log.includes('***')) {
                    // add extra filter condition
                    if (!filterLogs || (log.includes('INFO') || log.includes('.json') || log.includes('.pkg') || log.includes('.png'))) {
                        filteredData.push(log);
                    }
                }
            });
  
              if (latestIP && latestUserAgent) {
                  setClientIP(latestIP);
                  setUserAgent(latestUserAgent);
              }
  
              setLogs(filteredData);
          } else {
              console.error('Received data is not an array:', data);
              setLogs([]);
          }
      } catch (error) {
          console.error('Failed to fetch logs:', error);
          setLogs([]);
      }
  };


    //LOG Update every * seconds
    useEffect(() => {
      const interval = setInterval(fetchLogs, 1000); //1 seconds
      return () => clearInterval(interval);
  }, [filterLogs]);
    
    //auto scroll switch
    const [autoScroll, setAutoScroll] = useState(true);
    const AutoScrollChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAutoScroll(e.target.checked);
      };

    //LOG scroll to bottom auto
    const previousLogLength = useRef<number>(0);
    useEffect(() => {
      if (logRef.current && autoScroll) {
        // scroll when the log array length 
        if (logs.length > previousLogLength.current) {
          logRef.current.scrollTop = logRef.current.scrollHeight;
        }
        //update the previous log length
        previousLogLength.current = logs.length;
      }
    }, [logs, autoScroll]);  
    
   
     
////////////////////////JSON INPUT AREA/////////////////////////////////////

    //json link is invalid?  get game cover and  game info
    const [animateText, setAnimateText] = useState(false);//game info text animat
    const [jsonInput, setJsonInput] = useState('');
    const [jsonInputFeedback, setJsonInputFeedback] = useState(t('m1jsoninput'));
    const [backgroundImage, setBackgroundImage] = useState('');
    

    //if  user input json valid,Game info will be shown,and game cover.
    const JsonInputChange = async (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const input = e.target.value;
      setJsonInput(input);
      if (input.trim() === '') {
          setJsonInputFeedback(t('m1jsoninput'));
          setGameInfo(prev => ({ ...prev, imageUrl: '' }));
          setAnimateText(false);
          setBackgroundImage('');
      } else {
          const feedback = validateJsonInput(input);
          setJsonInputFeedback(feedback);
          if (feedback.includes('😊')) {
              setBackgroundImage(correctBackground);
              setAnimateText(true);
              setTimeout(() => setAnimateText(false), 1000);
              if (mode === 1) {  // confirmm mode 1
                  try {
                      const gameDetailsString = await SetMode(1, input);
                      if (typeof gameDetailsString !== 'string') {
                          throw new Error("Received non-string response from SetMode.");
                      }
                      const gameDetails = JSON.parse(gameDetailsString);
                      setGameInfo({
                          gameName: gameDetails.GameName,
                          gameId: gameDetails.CUSA,
                          region: gameDetails.Region,
                          lastVersion: gameDetails.LastVersion,
                          downgradeVersion: await ExtractVersion(input),
                          imageUrl: await TitleMetadataInfo(input)
                      });
                  } catch (error) {
                      console.error('Failed to update game info:', error);
                      setGameInfo(prev => ({ ...prev, imageUrl: noCover }));
                  }
              }
          }else{
            setBackgroundImage(incorrectBackground);
          }
      }
  };

    ///////////image loaded/////////
    const [imageLoaded, setImageLoaded] = useState(false);
    const imageLoad = () => {
      setImageLoaded(true);
      setTimeout(() => {
        setImageLoaded(false); 
      }, 2000); // glitch animation duration
    };
    const imageClick = () => {
      if (gameInfo.imageUrl !== waitImage && gameInfo.imageUrl !== noCover) {
          OpenBrowser(gameInfo.imageUrl);
      }
  };


    //////////////mode change////////////
    const [modeSelectEnable, setModeSelectEnable] = useState(true);
    const [ShowCantSelectModeToast, setShowCantSelectModeToast] = useState(false);
    const ModeChange = async (newMode: number) => {
    if (!serverRunning && modeSelectEnable) {
        setMode(newMode);
        if (newMode === 1) {
            await OtherLog(1); 
        }
        if (newMode === 2) {
            // mode 2 use empty json link
            try {
                await SetMode(2, "");
               
            } catch (error) {
                console.error('Failed to set mode 2:', error);
            }
        }
    } else {
        setShowCantSelectModeToast(true);
        setTimeout(() => setShowCantSelectModeToast(false), 2000);
    }
  };
    
  

  ////////////////server running///////////////////
  const [serverStatusMsg, setServerStatusMsg] = useState(t('servernotrunning'));
  const [serverRunning, setServerRunning] = useState(false);
  const [showModeWarning, setShowModeWarning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progressActive, setProgressActive] = useState(false);
  const checkServerError = async () => { //check if the server start failed
    const response = await fetch('http://localhost:29090/last-server-error');
    if (!response.ok) {
        throw new Error(await response.text());
    }
    const text = await response.text();
    if (text !== "No error") {
        throw new Error(text);
    }
};
  

const toggleServer = async () => {
  if (serverRunning) {  //stop sever
      setLoading(true);
      await StopProxy();
      setServerRunning(false);
      setServerStatusMsg(t('servernotrunning'));
      setLoading(false);
      setModeSelectEnable(true);

  } else { //start server
      if (mode !== 1 && mode !== 2) {
          setShowModeWarning(true);
          setTimeout(() => setShowModeWarning(false), 2000);//“NoModeSelectedWarning” duration time
      }

      const portAvailable = await CheckPort(serverPort);
      if (portAvailable) {
          setAlertMsg(t('portused'));
          showAlertWithDelay();
          return;
      }

      if (mode === 1 && !validateJsonInput(jsonInput).includes('😊')) {
          setAlertMsg(t('plsinputjson'));
          showAlertWithDelay();
          return;
      }

        setProgressActive(true); 
        setLoading(true);
        setModeSelectEnable(false);

        setTimeout(async () => {
            await StartProxy(serverPort.toString());
            const error = await GetLastServerError();
            if (error) {
                setShowAlert(true);
                setAlertMsg(t('serverstartfailed'));
                setProgressActive(false);
                setLoading(false);
                setServerRunning(false);// 如果启动失败，重置服务器状态
                setModeSelectEnable(true);
            } else {
                setServerRunning(true);
                setServerStatusMsg(t('serverrunning'));
                setProgressActive(false);
                setLoading(false);
            }
        }, 2000);
  }
};


       
///////////////footer/////////////////
//guide button
const GuideClick = async (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
  event.preventDefault();  // prevent <a> tag default behavior, avoid reload page
  try {
      const url = getGuideUrl();
      await OpenBrowser(url);
  } catch (error) {
      console.error('Failed to open URL:', error);
  }
};

//faqs
const [showFAQModal, setShowFAQModal] = useState(false);

    const toggleFAQModal = () => {
        setShowFAQModal(!showFAQModal);
    };

///////////some text baffle animation//////////
    //baffle
    //custom chara
    const bricks = '░░▒▓█';
    const lines = '├─┼┴┬┤';
    const waves = ' ﹊﹍﹎﹋﹌﹏';
    const devil = '魑魅魍魎';

    // for game details baffle
    const gameNameRef = useRef<HTMLParagraphElement>(null);
    const gameIdRef = useRef<HTMLParagraphElement>(null);
    const gameRegionRef = useRef<HTMLParagraphElement>(null);
    const gameLastVersionRef = useRef<HTMLParagraphElement>(null);
    const gameDowngradeVersionRef = useRef<HTMLParagraphElement>(null);
  
    useEffect(() => { //avoid  game info display not update
      if (gameIdRef.current && gameNameRef.current) {
        gameIdRef.current.textContent = gameInfo.gameId + ' - ' + gameInfo.region;
        gameNameRef.current.textContent = gameInfo.gameName;
      }
    }, [gameInfo]); 

    //game details baffle animation
    useEffect(() => {
  const baffleOptions = {
    characters: lines+bricks+waves,
    speed: 75
    };
  const baffleTexts = [
    gameNameRef.current,
    gameIdRef.current,
    gameRegionRef.current,
    gameLastVersionRef.current,
    gameDowngradeVersionRef.current
    ].filter(el => el !== null) // Filter out null values
      .map(el => baffle(el!, baffleOptions)); 

    baffleTexts.forEach((baffleText, index) => {
      setTimeout(() => {
      baffleText.start();
      setTimeout(() => {
        baffleText.reveal(1000); //animation duration
      }, 100);
      }, index * 500);//animation delay
      });
      }, [gameInfo]); // Re-run animation when gameInfo changes


   //server status baffle animation
   const serverStatusRef = useRef<HTMLParagraphElement>(null);
   useEffect(() => {
     if (serverRunning && serverStatusRef.current) {
         const baffleText = baffle(serverStatusRef.current, {
             characters: 'yurisa',
             speed: 75
         });
         baffleText.start();
         setTimeout(() => {
             baffleText.reveal(800);
         }, 800); // delay 1s start,after the loading bar complete 
     }
       }, [serverRunning]);

   //log baffle animation
  const previousLogsLength = useRef(logs.length);
  const contentRefs = useRef<(HTMLDivElement | HTMLSpanElement | null)[]>([]);

  // when logs update,apply baffle animation
  useEffect(() => {
    const newLogsCount = logs.length - previousLogsLength.current;
    if (newLogsCount > 0) {
      contentRefs.current.slice(-newLogsCount).forEach(contentRef => {
        if (contentRef) {
          const b = baffle(contentRef, {
            characters: waves,
            speed: 75
          });
          b.start();
          setTimeout(() => b.reveal(100), 50);
        }
      });
    }
    previousLogsLength.current = logs.length;
    contentRefs.current = contentRefs.current.slice(0, logs.length);
  }, [logs]);



  ///////////////////////////////frontend interface/////////////////////////////////////
  //main content

    return (
      <div className={`app  crt-bg custom-bg ${fontClass(i18n.language)}`}>
        {showFAQModal && (//FAQ
            <>
                <div className="overlay" onClick={toggleFAQModal}></div>
                <div className="faq-modal">
                    <span className="close" onClick={toggleFAQModal}>&times;</span>
                   
                    <h2>{t('ErrorCode')}</h2>
                    <div id='faq-content'>
                    <p className='crt-bg'><b>PS5 :</b><br/>
                    <div id='code' className='red font-seiha'>CE-107893-8</div> {t('CUSAMismatch')}<br/>
                    <div id='code' className='red font-seiha'>CE-107889-3</div>  {t('SpecialIssue')}<br/>
                    <div id='code' className='red font-seiha'>NW-102650-4</div>  {t('Blocked')}<br/>
                    <div id='code' className='red font-seiha'>NW-102261-2</div>  {t('Blocked2')}<br/>
                    </p>
                    <p className='crt-bg'><b>PS4 :</b><br/>
                    <div id='code' className='red font-seiha'>NW-31468-2</div>  {t('Blocked_PS4')}<br/>
                    <div id='code' className='red font-seiha'>CE-36246-1</div>  {t('CUSAMismatch')}<br/>
                    <div id='code' className='red font-seiha'>NW-31472-7</div>  {t('neterror')}<br/>
                    </p>
                    <p className='crt-bg'>{t('other_error')}<br/>
                     {t('other_error1')}<br/>
                     {t('other_error2')}
                    </p>
                    </div>
                </div>
            </>
        )}

        {showAlert && ( //show alert popup
                <>
                    <div className="overlay crt" onClick={closeAlert}></div>
                    <div className="alert">
                        <div className="alert-content">
                            <p>{alertMsg}</p>
                        </div>
                        <button onClick={closeAlert} className='crt'>OK</button>
                    </div>
                </>
            )}    
        
        <div className="header">
          <div className="logo">
            <img  src={kb} />
          </div>
        </div>

        <div className="device-info font-seiha">
        <h5 className='animated-text-reveal  '>{t('Connected')}</h5>
        <div id='device-list'>
        <p >
          IP : <span id='ip'>{clientIP}</span>
          {t('type')} : <span id='device'>{userAgent}</span><br/>

          </p>
          
          </div>
        </div>
      
        <div className="main-content">
        <div className="top-row">
        <div id="mode1" className={`mode-selection  ${mode === 1 ? 'active' : ''} ${mode === 2 ? 'dimmed' : ''} animated-border`} onClick={() => ModeChange(1)}>
        <svg className="border-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline className="keyline keyline1" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
        </svg>
        <h2 className='animated-text-reveal font-seiha'>{t('Mode1')}</h2>
        <p className="reveal-text">{t('Mode1Desc')}</p>
        </div>
        <div id="mode2" className={`mode-selection  ${mode === 2 ? 'active' : ''} ${mode === 1 ? 'dimmed' : ''} animated-border`} onClick={() => ModeChange(2)}>
        <svg className="border-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline className="keyline keyline2" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
        </svg>
        <h2 className='animated-text-reveal font-seiha'>{t('Mode2')}</h2>
        <p className="reveal-text">{t('Mode2Desc')}</p>
        </div>
      </div>

      <div className="server animated-border">
        <svg className="border-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline className="keyline keyline1" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
        </svg>
        <h2 className='animated-text-reveal font-seiha'>{t('ProxyServer')}</h2>
        <div className="server-inputs rajdhani-semibold">
        <label className='font-seiha'>
          <span>{t('LocalIP')}</span>
          <input
              className={`font-seiha server-input-color ${serverRunning ? 'red' : ''}`}
              type="text"
              value={serverIp}
              onChange={(e) => setServerIp(e.target.value)}
              disabled/>
        </label>
        <label className='font-seiha'>
        <span className='font-seiha'>{t('Port')}</span>
        <input
        className={`input-hover font-seiha server-input-color ${serverRunning ? 'red' : ''}`}
        type="number"
        value={serverPort}
        onChange={(e) => setServerPort(Number(e.target.value))}
        disabled={serverRunning}
        min={1024}
        max={65535}
        />
        </label>
      
      </div>
      
      <p id="server-status" ref={serverStatusRef} className={`animated-text-reveal ${serverRunning ? "running red" : ""}`}>
        {serverStatusMsg}
      </p>
      <button 
         className={`btn crt-static ${serverRunning ? 'btn-slash' : ''}`} 
         onClick={toggleServer}>
          <div className={` ${progressActive ? 'btn-progress' : ''}`} style={{ height: '100%', width: '100%' }}>
          {!progressActive && <span>{serverRunning ? t("StopProxy") : t("StartProxy")}</span>}
          </div>
      </button>

      </div>
      </div>
        
      <div className="main-content-low">
        <div className="left-panel">
        {mode === 0 && (
              <div className="mode0 animated-border">
                <svg className="border-svg-s" viewBox="0 0 100 100" preserveAspectRatio="none">
              <polyline className="keyline keyline4" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
              </svg>
                <p className='animated-text-reveal  mode0-text'>{t('PleaseSelectAnyMode')}</p>
                <img src={mode0} className={`mode0-img ${imageLoaded ? 'glitch' : ''}`} />
              </div>
            )}
          {mode === 1 && (
            <div className="mode1  animated-border">
              <label>
              <svg className="border-svg-s" viewBox="0 0 100 100" preserveAspectRatio="none">
              <polyline className="keyline keyline4" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
              </svg>
              <b><span id="json-input-info" className='animated-text-reveal'>{jsonInputFeedback}</span></b>
                <textarea
                className='input-hover font-en'
                id="json-input"
                value={jsonInput}
                onChange={JsonInputChange}
                 placeholder=""
                 disabled={serverRunning}
                 style={{ backgroundImage: `url(${backgroundImage})` }}
                />
              </label>
              <div className="mode1-content">
              <img
              id="game-image"
              className={` ${imageLoaded ? 'glitch' : ''}`}
              onLoad={imageLoad}
              onError={() => setGameInfo(prev => ({ ...prev, imageUrl: noCover }))}
              src={gameInfo.imageUrl}
              onClick={imageClick}
              style={{ cursor: gameInfo.imageUrl !== noCover ? 'pointer' : 'default' }}
              />
                <div className="game-info" id="game-info">
                    <p className="game-detail-k">{t('GameName')}:</p>
                    <p ref={gameNameRef} className="game-detail-v red">{gameInfo.gameName}</p>
                    <p className="game-detail-k">{t('GameIDRegion')}:</p>
                    <p ref={gameIdRef} className="game-detail-v red">{gameInfo.gameId} - {gameInfo.region}</p>
                    <p className="game-detail-k">{t('LastVersion')}:</p>
                    <p ref={gameLastVersionRef} className="game-detail-v red">{gameInfo.lastVersion}</p>
                    <p className="game-detail-k">{t('DowngradeVersion')}:</p>
                    <b><p ref={gameDowngradeVersionRef} className="game-detail-v red">{gameInfo.downgradeVersion}</p></b>
                </div>
              </div>
            </div>
          )}
          {mode === 2 && (
            <div className="mode2 animated-border">
              <svg className="border-svg-s" viewBox="0 0 100 100" preserveAspectRatio="none">
              <polyline className="keyline keyline4" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
              </svg>
              <h4 className='animated-text-reveal font-seiha'>{t('Introduce')}</h4>
              <p className='reveal-text'>{t('m2desc1')}</p>
              <p className='reveal-text'>{t('m2desc2')}</p>
              <img src={kinshi} className={`mode2-img ${imageLoaded ? 'glitch' : ''}`} />
            </div>
          )}
        </div>
        <div className="right-panel">
          <div className="log animated-border">
          <svg className="border-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline className="keyline keyline1" points="0,0 100,0 100,100 0,100 0,0" fill="none" stroke="#777" strokeWidth="0.5"/>
          </svg>

          <div className="log-header">
              <b><p className='animated-text-reveal crt font-seiha'>{t('LOG')}</p></b>
              <div className="auto-scroll-container">
              <input
                   type="checkbox"
                    checked={autoScroll}
                    onChange={AutoScrollChange}
                    className="auto-scroll-checkbox"
               />
              <span className='auto-scroll-text'>{t('AutoScroll')}</span>
        
              <input
                  type="checkbox"
                  checked={filterLogs}
                  onChange={FilterLogsChange}
                  className="auto-scroll-checkbox"
              />
                  <span className='auto-scroll-text'>{t('LogFiltering')}</span>
              </div>
            </div>
            
            <div className="log-container font-log" ref={logRef}>
      {logs.length > 0 ? logs.map((logEntry, idx) => {
        const parts = logEntry.split('-');
        if (parts.length < 3) return null;
        const time = parts[0].trim();
        const type = parts[1].trim();
        const message = parts.slice(2).join('-').trim();

        // 使用正则表达式检测 URL
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const messageWithLinks = message.replace(urlRegex, (url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);

        if (!contentRefs.current[idx]) {
          contentRefs.current[idx] = null;
        }

        return (
          <div key={idx} className="log-entry">
            <span className="log-time">{time}</span>
            <span className={`log-type ${type === 'INFO' ? 'log-info' : ''} ${type === 'ERROR' ? 'log-error' : ''}`}>{type}</span>
            <span className="log-message" ref={el => contentRefs.current[idx] = el} dangerouslySetInnerHTML={{ __html: messageWithLinks }}></span>
          </div>
        );
      }) : <div>{t('NoLogsAvailable')}</div>}
    </div>

          <div className="log-footer">
            <span className='red' onClick={toggleFAQModal}>{t('ErrorCode')}</span>
            <span id='guide'>
                <a className='red' href={getGuideUrl()} onClick={GuideClick}>{t('guide')}</a>
            </span>
          </div>
          </div>
          </div>
      </div>
              {ShowCantSelectModeToast && <div className="toast"><p className='crt-static'>{t('ServerRunningCannotSelectMode')}</p></div>}
              {showModeWarning && <div className="toast crt-static"><p>{t('NoModeSelectedWarning')}</p></div>}
    </div>
  );
};

export default App;