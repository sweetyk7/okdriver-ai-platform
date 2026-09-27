import React, { useState, useEffect } from 'react';

export default function LiveClock() {
  const [time, setTime] = useState(new Date().toLocaleTimeString('en-IN'));
  useEffect(() => {
    const t = setInterval(() => setTime(new Date().toLocaleTimeString('en-IN')), 1000);
    return () => clearInterval(t);
  }, []);
  return <span>{new Date().toLocaleDateString('en-IN')} {time}</span>;
}
