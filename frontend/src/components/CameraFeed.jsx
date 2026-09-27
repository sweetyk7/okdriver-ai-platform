import React, { useState, useRef, useEffect } from 'react';
import API from '../utils/api';
import { getDummyVideo } from '../utils/constants';
import LiveClock from './LiveClock';

export default function CameraFeed({ feed, large = false }) {
  const feedRef = useRef(null);
  const videoRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    let pc = null;
    
    const startWebRTC = async () => {
      if (!feed.stream_url) return;
      
      pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });
      
      pc.ontrack = (event) => {
        if (videoRef.current) {
          videoRef.current.srcObject = event.streams[0];
        }
      };
      
      pc.addTransceiver('video', { direction: 'recvonly' });
      
      try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        
        const res = await API.post(`/cameras/${feed.camera_id}/webrtc/offer`, {
          sdp: pc.localDescription.sdp,
          type: pc.localDescription.type
        });
        
        await pc.setRemoteDescription(res.data);
      } catch (err) {
        console.error("WebRTC Setup Failed", err);
      }
    };
    
    startWebRTC();
    
    return () => {
      if (pc) {
        pc.close();
      }
    };
  }, [feed.camera_id, feed.stream_url]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      feedRef.current?.requestFullscreen().catch(err => console.log(err));
    } else {
      document.exitFullscreen();
    }
  };

  const takeSnapshot = async () => {
    setFlash(true);
    setTimeout(() => setFlash(false), 200);
    try {
      await API.post(`/cameras/${feed.camera_id}/snapshot`);
    } catch (err) {
      console.error("Snapshot failed", err);
    }
  };

  const toggleRecording = async () => {
    try {
      const action = isRecording ? "stop" : "start";
      const res = await API.post(`/cameras/${feed.camera_id}/record?action=${action}`);
      if (res.data.message) setIsRecording(!isRecording);
    } catch (err) {
      console.error("Recording failed", err);
    }
  };

  return (
    <div ref={feedRef} className={`video-feed ${large ? 'video-feed-large' : ''}`}>
      {flash && <div style={{ position: 'absolute', inset: 0, background: 'white', zIndex: 10, opacity: 0.8 }} />}

      {feed.stream_url ? (
        <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      ) : (
        <video autoPlay muted loop playsInline>
          <source src={getDummyVideo(feed.camera_id)} type="video/mp4" />
        </video>
      )}

      <div className="video-top-label">
        <span>{feed.camera_id} | {feed.department_name || 'General'}</span>
        <LiveClock />
      </div>

      <div className="video-toolbar">
        <button onClick={toggleRecording} className={isRecording ? 'recording-active' : ''} title="Record">
          <span className="live-dot" style={{ display: isRecording ? 'inline-block' : 'none' }}></span>
          {isRecording ? 'STOP' : 'REC'}
        </button>
        <button onClick={takeSnapshot} title="Take Snapshot">📸</button>
        <button onClick={toggleFullscreen} title="Fullscreen">⛶</button>
      </div>

      <div className="video-label">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="live-dot" /> LIVE
        </span>
        <span>{feed.name}</span>
      </div>
    </div>
  );
}
