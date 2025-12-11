import React, { useState, useEffect } from 'react';
import { 
  Cloud, CloudRain, AlertTriangle, MapPin, TrendingUp, 
  Droplets, Wind, Thermometer, CloudDrizzle, Activity, 
  Timer, Radio, Satellite, Signal, Database, Globe, Scan, Info,
  Cpu, Share2, Anchor, Battery, Wifi, Navigation, Power, CheckCircle2,
  User, Lock, Mail, Phone, ArrowRight, ChevronRight
} from 'lucide-react';

// --- HELPER COMPONENTS ---

const GlassCard = ({ children, className = "" }) => (
  <div className={`bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl rounded-3xl p-6 ${className}`}>
    {children}
  </div>
);

const Thermometer3D = ({ temp }) => {
  const percent = Math.min(Math.max((temp / 50) * 100, 15), 90);
  return (
    <div className="relative w-12 h-32 flex flex-col items-center justify-end">
      <div className="w-4 h-full bg-white/5 rounded-t-full border border-white/20 backdrop-blur-sm relative overflow-hidden z-10 shadow-inner">
          <div className="absolute top-0 left-1 w-1 h-full bg-white/20 blur-[1px] z-20"></div>
          <div 
              className="absolute bottom-0 w-full bg-gradient-to-t from-red-700 via-red-500 to-red-400 transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(239,68,68,0.6)]"
              style={{ height: `${percent}%` }}
          >
              <div className="w-full h-1 bg-red-300 rounded-full opacity-80 absolute top-0"></div>
          </div>
      </div>
      <div className="w-10 h-10 -mt-3 rounded-full bg-gradient-to-br from-red-500 via-red-600 to-red-800 border border-red-400/30 shadow-[0_0_20px_rgba(220,38,38,0.5)] z-20 relative flex items-center justify-center">
           <div className="absolute top-2 left-2 w-3 h-3 bg-white/40 rounded-full blur-[2px]"></div>
      </div>
      <div className="absolute right-0 top-2 bottom-10 w-1 flex flex-col justify-between py-1 pointer-events-none">
          {[50, 40, 30, 20, 10].map((t) => (
              <div key={t} className="flex items-center gap-1">
                  <div className="w-1.5 h-[1px] bg-white/30"></div>
              </div>
          ))}
      </div>
    </div>
  );
};

const CondensationBackground = () => (
  <div className="absolute inset-0 z-0 opacity-20 pointer-events-none mix-blend-overlay">
    <svg className="w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
      <circle cx="10" cy="10" r="2" fill="white" />
      <circle cx="25" cy="40" r="1.5" fill="white" />
      <circle cx="40" cy="15" r="2.5" fill="white" />
      <circle cx="60" cy="50" r="1" fill="white" />
      <circle cx="80" cy="20" r="2" fill="white" />
      <path d="M 30 15 Q 32 30 30 45" stroke="white" strokeWidth="1" fill="none" opacity="0.6" strokeLinecap="round" />
      <path d="M 90 20 Q 92 40 90 60" stroke="white" strokeWidth="1" fill="none" opacity="0.5" strokeLinecap="round" />
    </svg>
  </div>
);

const HumidityDroplet = ({ humidity }) => {
  const fillHeight = Math.min(Math.max(humidity, 0), 100);
  return (
    <div className="relative w-12 h-24 flex items-center justify-center -mt-2">
      <svg viewBox="0 0 100 160" className="w-full h-full drop-shadow-xl">
          <defs>
              <linearGradient id="waterGradient" x1="0" x2="0" y1="1" y2="0">
                  <stop offset="0%" stopColor="#1e40af" /> 
                  <stop offset="100%" stopColor="#60a5fa" />
              </linearGradient>
              <clipPath id="dropClip">
                   <path d="M50 0 C50 0 100 80 100 110 C100 137.6 77.6 160 50 160 C22.4 160 0 137.6 0 110 C0 80 50 0 50 0 Z" />
              </clipPath>
          </defs>
          <path d="M50 0 C50 0 100 80 100 110 C100 137.6 77.6 160 50 160 C22.4 160 0 137.6 0 110 C0 80 50 0 50 0 Z" 
                fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.2)" strokeWidth="3" />
          <g clipPath="url(#dropClip)">
              <rect x="0" y={160 - (1.6 * fillHeight)} width="100" height="160" fill="url(#waterGradient)" className="transition-all duration-1000 ease-out" />
              <path d={`M0 ${160 - (1.6 * fillHeight)} Q 50 ${160 - (1.6 * fillHeight) + 10} 100 ${160 - (1.6 * fillHeight)}`} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
          </g>
          <path d="M30 40 Q 15 80 15 120" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="3" strokeLinecap="round" />
      </svg>
    </div>
  );
};

const LeafProgress = ({ value, color }) => {
  const leafPath = "M50 5 C50 5 90 40 90 70 C90 90 75 100 50 100 C25 100 10 90 10 70 C10 40 50 5 50 5 Z";
  return (
    <div className="relative flex items-center justify-center">
      <div className={`absolute inset-0 rounded-full blur-3xl opacity-30`} style={{ backgroundColor: color }}></div>
      <svg className="w-40 h-40 relative z-10" viewBox="0 0 100 105">
        <defs>
          <linearGradient id="leafFill" x1="0" x2="0" y1="1" y2="0">
            <stop offset={`${value}%`} stopColor={color} />
            <stop offset={`${value}%`} stopColor="rgba(255,255,255,0.1)" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        <path d={leafPath} fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="3" />
        <path d={leafPath} fill="url(#leafFill)" className="transition-all duration-1000 ease-in-out" filter="url(#glow)" />
        <path d="M50 20 L50 90" stroke="rgba(255,255,255,0.1)" strokeWidth="1" strokeLinecap="round" />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-white z-20 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/3">
        <span className="text-3xl font-bold tracking-tighter drop-shadow-md">{value}%</span>
      </div>
    </div>
  );
};

const Aerostat = () => (
  <div className="absolute right-4 top-0 w-48 h-full pointer-events-none z-0 opacity-100 overflow-visible">
     <div className="w-full h-full animate-aerostat-deploy">
        <div className="w-full h-full animate-aerostat-float flex flex-col items-center pt-8">
           <svg viewBox="0 0 200 600" className="w-full h-[600px] drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
              <defs>
                <radialGradient id="cloudGrad" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(255,255,255,0.4)" />
                    <stop offset="100%" stopColor="rgba(255,255,255,0)" />
                </radialGradient>
              </defs>
              <g className="animate-cloud-drift-1">
                  <path d="M10,80 Q30,60 50,80 T90,80" fill="url(#cloudGrad)" opacity="0.3" />
                  <path d="M120,60 Q140,40 160,60 T200,60" fill="url(#cloudGrad)" opacity="0.2" />
              </g>
              <line x1="100" y1="180" x2="100" y2="1000" stroke="#94a3b8" strokeWidth="2" />
              <g>
                  <ellipse cx="100" cy="100" rx="80" ry="45" fill="#f1f5f9" stroke="#94a3b8" strokeWidth="1" />
                  <path d="M20,100 Q100,50 180,100" fill="none" stroke="#cbd5e1" strokeWidth="1" />
                  <path d="M20,100 L0,125 L30,125 Z" fill="#334155" stroke="#1e293b" strokeWidth="1"/>
                  <path d="M180,100 L200,125 L170,125 Z" fill="#334155" stroke="#1e293b" strokeWidth="1"/>
                  <rect x="75" y="140" width="50" height="20" rx="4" fill="#1e293b" stroke="#334155" strokeWidth="1" />
                  <circle cx="100" cy="150" r="3" fill="#ef4444">
                      <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite" />
                  </circle>
              </g>
              <g className="animate-cloud-drift-2">
                  <path d="M-20,130 Q10,110 40,130 T100,130" fill="url(#cloudGrad)" opacity="0.4" />
                  <path d="M150,110 Q180,90 210,110" fill="url(#cloudGrad)" opacity="0.3" />
              </g>
           </svg>
        </div>
     </div>
  </div>
);

const DroneFleet = () => {
    const Drone = ({ className }) => (
        <svg viewBox="0 0 100 60" className={`w-16 h-10 ${className}`}>
            <defs>
                <filter id="droneGlow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <ellipse cx="50" cy="30" rx="15" ry="5" fill="#3b82f6" stroke="#60a5fa" filter="url(#droneGlow)" />
            <path d="M20,30 L80,30" stroke="#94a3b8" strokeWidth="2" />
            <path d="M50,30 L50,30" stroke="#94a3b8" strokeWidth="2" />
            <ellipse cx="20" cy="30" rx="12" ry="2" fill="rgba(255,255,255,0.5)" className="animate-spin-fast origin-[20px_30px]" />
            <ellipse cx="80" cy="30" rx="12" ry="2" fill="rgba(255,255,255,0.5)" className="animate-spin-fast origin-[80px_30px]" />
            <circle cx="50" cy="32" r="2" fill="#ef4444" className="animate-pulse" />
            <circle cx="20" cy="32" r="1" fill="#10b981" />
            <circle cx="80" cy="32" r="1" fill="#10b981" />
        </svg>
    );

    return (
        <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
            <div className="absolute left-[40%] bottom-0 w-16 h-16 animate-drone-launch-1">
                 <div className="animate-drone-hover-1">
                     <Drone className="" />
                 </div>
            </div>
            <div className="absolute left-[15%] bottom-0 w-12 h-12 animate-drone-launch-2">
                 <div className="animate-drone-hover-2">
                    <Drone className="scale-75 opacity-80" />
                 </div>
            </div>
            <div className="absolute left-[65%] bottom-0 w-12 h-12 animate-drone-launch-3">
                 <div className="animate-drone-hover-3">
                    <Drone className="scale-75 opacity-80" />
                 </div>
            </div>
        </div>
    );
};


const MultiLineChart = ({ datasets, timestamps, className }) => {
  if (!datasets || datasets.length === 0) return null;
  const length = datasets[0].data.length;
  if (length < 2) return null;

  const normalize = (val, min, max) => {
      const range = max - min || 1;
      return ((val - min) / range) * 65; 
  };

  return (
      <div className={`w-full ${className}`}>
          <div className="flex justify-center gap-6 mb-4">
              {datasets.map((ds, i) => (
                  <div key={i} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: ds.color }}></div>
                      <span className="text-xs font-bold text-white/70 uppercase tracking-wide">{ds.label}</span>
                  </div>
              ))}
          </div>

          <div className="h-48 w-full overflow-visible">
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full overflow-visible">
                  {Array.from({ length }).map((_, i) => {
                      const x = (i / (length - 1)) * 100;
                      const isStart = i === 0;
                      const isEnd = i === length - 1;
                      const isInterval = i % 5 === 0;

                      if (isStart || isEnd || isInterval) {
                          let textAnchor = "middle";
                          if (isStart) textAnchor = "start";
                          if (isEnd) textAnchor = "end";

                          return (
                              <g key={i}>
                                  <line x1={x} y1="0" x2={x} y2="80" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" strokeDasharray="2" />
                                  {timestamps && timestamps[i] && (
                                      <text x={x} y="95" fontSize="3.5" fill="rgba(255,255,255,0.3)" textAnchor={textAnchor} className="font-mono font-medium">
                                          {timestamps[i]}
                                      </text>
                                  )}
                              </g>
                          );
                      }
                      return null;
                  })}

                  {datasets.map((ds, idx) => {
                      const min = Math.min(...ds.data);
                      const max = Math.max(...ds.data);
                      
                      const points = ds.data.map((val, i) => {
                          const x = (i / (length - 1)) * 100;
                          const y = 75 - normalize(val, min, max); 
                          return `${x},${y}`;
                      }).join(' ');

                      return (
                          <polyline
                              key={idx}
                              fill="none"
                              stroke={ds.color}
                              strokeWidth="2"
                              points={points}
                              vectorEffect="non-scaling-stroke"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="drop-shadow-lg"
                          />
                      );
                  })}
              </svg>
          </div>
      </div>
  );
};

// --- LOGIN PAGE COMPONENT ---
const LoginPage = ({ onLogin }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.name || !formData.password) {
      setError('Name and Password are required');
      return;
    }
    
    if (isRegistering) {
        if (!formData.phone || !formData.email) {
            setError('All fields are required for registration');
            return;
        }
    }
    
    // Simulate auth delay
    setTimeout(() => {
        onLogin(formData.name);
    }, 500);
  };

  return (
    <div className="flex items-center justify-center min-h-screen px-4">
       <GlassCard className="w-full max-w-md p-8 relative z-10 border-white/20">
          {/* Logo & Title */}
          <div className="flex flex-col items-center mb-8">
             <div className="p-4 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl shadow-lg shadow-cyan-500/20 mb-4 animate-in zoom-in duration-500">
                <CloudRain className="w-10 h-10 text-white" />
             </div>
             <h1 className="text-3xl font-bold tracking-tight text-white">StormEye</h1>
             <p className="text-blue-200 text-sm font-medium tracking-wide">Autonomous Sensor Network</p>
          </div>

          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-2">
                {isRegistering ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="text-white/50 text-sm">
                {isRegistering ? 'Join the network to monitor severe weather.' : 'Enter your credentials to access the dashboard.'}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-500/20 border border-red-500/40 rounded-xl flex items-center gap-3 text-red-200 text-sm">
                <AlertTriangle size={16} />
                {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
             {/* Name Input */}
             <div className="space-y-1">
                <label className="text-xs font-bold text-blue-200 uppercase tracking-wider ml-1">Name</label>
                <div className="relative group">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-cyan-400 transition-colors" size={18} />
                    <input 
                        type="text" 
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-black/50 transition-all"
                        placeholder="Enter your name"
                    />
                </div>
             </div>

             {/* Registration Fields */}
             {isRegistering && (
                 <>
                    <div className="space-y-1 animate-in slide-in-from-top-2 fade-in duration-300">
                        <label className="text-xs font-bold text-blue-200 uppercase tracking-wider ml-1">Phone Number</label>
                        <div className="relative group">
                            <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-cyan-400 transition-colors" size={18} />
                            <input 
                                type="tel" 
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-black/50 transition-all"
                                placeholder="+91 98765 43210"
                            />
                        </div>
                    </div>

                    <div className="space-y-1 animate-in slide-in-from-top-2 fade-in duration-300 delay-75">
                        <label className="text-xs font-bold text-blue-200 uppercase tracking-wider ml-1">Email Address</label>
                        <div className="relative group">
                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-cyan-400 transition-colors" size={18} />
                            <input 
                                type="email" 
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-black/50 transition-all"
                                placeholder="name@example.com"
                            />
                        </div>
                    </div>
                 </>
             )}

             {/* Password Input */}
             <div className="space-y-1">
                <label className="text-xs font-bold text-blue-200 uppercase tracking-wider ml-1">Password</label>
                <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-cyan-400 transition-colors" size={18} />
                    <input 
                        type="password" 
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-black/50 transition-all"
                        placeholder="••••••••"
                    />
                </div>
             </div>

             <button 
                type="submit" 
                className="w-full mt-6 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
             >
                {isRegistering ? 'Create Account' : 'Sign In'}
                <ArrowRight size={18} />
             </button>
          </form>

          {/* Toggle */}
          <div className="mt-6 text-center text-sm text-white/60">
            {isRegistering ? 'Already have an account? ' : "Don't have an account? "}
            <button 
                onClick={() => { setIsRegistering(!isRegistering); setError(''); }}
                className="text-cyan-400 font-bold hover:text-cyan-300 hover:underline transition-colors"
            >
                {isRegistering ? 'Login' : 'Register'}
            </button>
          </div>
       </GlassCard>
    </div>
  )
}

export default function App() {
  // Authentication State
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userName, setUserName] = useState('');

  const [location, setLocation] = useState('Loni Kalbhor, Maharashtra');
  const [weatherData, setWeatherData] = useState({
    temperature: '28',
    humidity: '65',
    pressure: '1012',
    windSpeed: '12',
    rainfall: '0'
  });
  
  // Interactive Stage States
  const [stage2Active, setStage2Active] = useState(true);
  const [stage3Active, setStage3Active] = useState(false);

  // Helper to get current time string in 24h format
  const getTimeStr = (offsetSeconds = 0) => {
    const d = new Date();
    d.setSeconds(d.getSeconds() - offsetSeconds);
    return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  // History state for graphs
  const [history, setHistory] = useState({
    pressure: Array.from({ length: 20 }, () => 1010 + Math.random() * 5),
    humidity: Array.from({ length: 20 }, () => 60 + Math.random() * 10),
    wind: Array.from({ length: 20 }, () => 10 + Math.random() * 5),
    timestamps: Array.from({ length: 20 }, (_, i) => getTimeStr((19 - i) * 30)) 
  });

  const [satelliteData, setSatelliteData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [riskLevel, setRiskLevel] = useState('low');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [timeLeft, setTimeLeft] = useState(30);

  // --- AUTOMATION LOGIC ---
  useEffect(() => {
    if (!isAuthenticated) return; // Stop logic if not logged in

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          fetchSensorReadings(); 
          return 30; 
        }
        return prev - 1;
      });
    }, 1000);
    fetchSensorReadings();
    return () => clearInterval(timer);
  }, [isAuthenticated]);

  const fetchSensorReadings = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      const randomChance = Math.random();
      const isExtreme = randomChance > 0.8;

      let newHum, newPress, newWind, newRain;
      if (isExtreme) {
        newHum = (75 + Math.random() * 20).toFixed(1);
        newPress = (995 + Math.random() * 15).toFixed(0);
        newWind = (25 + Math.random() * 30).toFixed(1);
        newRain = (20 + Math.random() * 60).toFixed(1);
      } else {
        newHum = (40 + Math.random() * 30).toFixed(1);
        newPress = (1008 + Math.random() * 10).toFixed(0);
        newWind = (5 + Math.random() * 20).toFixed(1);
        newRain = (0 + Math.random() * 10).toFixed(1);
      }

      const newData = {
        temperature: (24 + Math.random() * 8).toFixed(0),
        humidity: newHum,
        pressure: newPress,
        windSpeed: newWind,
        rainfall: newRain
      };

      // Update history for graphs with new timestamp
      const newTime = getTimeStr();
      setHistory(prev => ({
        pressure: [...prev.pressure.slice(1), parseFloat(newPress)],
        humidity: [...prev.humidity.slice(1), parseFloat(newHum)],
        wind: [...prev.wind.slice(1), parseFloat(newWind)],
        timestamps: [...prev.timestamps.slice(1), newTime]
      }));

      const now = new Date();
      const newSatRows = Array.from({ length: 15 }).map((_, i) => {
        const cttBase = isExtreme ? -60 : -10; 
        const otBase = isExtreme ? 1.8 : 0.5;
        const moistBase = isExtreme ? 28 : 15;
        const riskVal = isExtreme ? 100 : Math.floor(Math.random() * 30);
        const riskLbl = riskVal > 80 ? 'Extreme' : riskVal > 40 ? 'Moderate' : 'Low';

        return {
            id: i,
            lat: (18.5 + (Math.random() * 0.1)).toFixed(2),
            lon: (74.0 + (Math.random() * 0.1)).toFixed(2),
            ctt: (cttBase + (Math.random() * 10 - 5)).toFixed(2),
            otIndex: (otBase + (Math.random() * 0.2)).toFixed(2),
            moistureFlux: (moistBase + Math.random()).toFixed(1),
            cii: ((isExtreme ? 18 : 10) + Math.random()).toFixed(1),
            riskLevel: riskLbl,
            timestamp: now.toISOString().substring(11, 16)
        };
      });

      setWeatherData(newData);
      setSatelliteData(newSatRows);
      runPredictionModel(newData); 
      setIsAnalyzing(false);
    }, 1500);
  };

  const runPredictionModel = (data) => {
    const { humidity, pressure, windSpeed, rainfall } = data;
    const h = parseFloat(humidity);
    const p = parseFloat(pressure);
    const w = parseFloat(windSpeed);
    const r = parseFloat(rainfall);
    let score = 0;
    
    if (h > 80) score += 30; else if (h > 70) score += 20;
    if (p < 1000) score += 25; else if (p < 1010) score += 15;
    if (w > 40) score += 25; else if (w > 30) score += 15;
    if (r > 50) score += 20; else if (r > 30) score += 15;

    let risk = 'low';
    if (score > 60) risk = 'high';
    else if (score > 35) risk = 'moderate';

    setPrediction(Math.min(score, 99));
    setRiskLevel(risk);
  };

  const getRiskGradient = (risk) => {
    switch(risk) {
      case 'high': return 'from-red-600/20 via-orange-600/10 to-red-900/5';
      case 'moderate': return 'from-yellow-500/20 via-orange-500/10 to-yellow-900/5';
      case 'low': return 'from-emerald-500/20 via-green-500/10 to-teal-900/5';
      default: return 'from-blue-500/20 via-cyan-500/10 to-blue-900/5';
    }
  };

  const getRiskColorHex = (risk) => {
    switch(risk) {
      case 'high': return '#ef4444';
      case 'moderate': return '#eab308';
      case 'low': return '#10b981';
      default: return '#3b82f6';
    }
  };

  // Scroll Handler
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Stage Handlers
  const toggleStage2 = (e) => {
    e.stopPropagation();
    const newState = !stage2Active;
    setStage2Active(newState);
    if (newState) setTimeout(() => scrollToSection('stage-2'), 100);
  };

  const toggleStage3 = (e) => {
    e.stopPropagation();
    const newState = !stage3Active;
    setStage3Active(newState);
    if (newState) setTimeout(() => scrollToSection('stage-3'), 100);
  };

  const handleLoginSuccess = (name) => {
      setUserName(name);
      setIsAuthenticated(true);
  };

  // --- RENDER LOGIC ---

  if (!isAuthenticated) {
      return (
        <div className="min-h-screen font-sans text-white bg-slate-900 bg-fixed bg-cover bg-center selection:bg-cyan-500/30"
             style={{ backgroundImage: `url('https://images.unsplash.com/photo-1516912481808-542336eb8794?q=80&w=2400&auto=format&fit=crop')` }}>
           
           <div className="fixed inset-0 bg-black/40 backdrop-blur-sm pointer-events-none"></div>
           <LoginPage onLogin={handleLoginSuccess} />
        </div>
      );
  }

  return (
    <div className="min-h-screen font-sans text-white bg-slate-900 bg-fixed bg-cover bg-center selection:bg-cyan-500/30"
         style={{ backgroundImage: `url('https://images.unsplash.com/photo-1516912481808-542336eb8794?q=80&w=2400&auto=format&fit=crop')` }}>
      
      {/* Lightened Overlay - Changed from black tint to subtle white tint */}
      <div className="fixed inset-0 bg-white/5 pointer-events-none"></div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl shadow-lg shadow-cyan-500/20">
                <CloudRain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-white drop-shadow-md">
                  StormEye
                </h1>
                <p className="text-sm text-blue-200 flex items-center gap-2 font-medium">
                  <Activity className="w-4 h-4" />
                  Autonomous Sensor Network
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* User Profile Badge */}
              <div className="hidden md:flex items-center gap-3 bg-white/5 px-4 py-2 rounded-xl border border-white/10 mr-2">
                 <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-sm font-bold">
                     {userName.charAt(0).toUpperCase()}
                 </div>
                 <div className="text-sm font-medium">{userName}</div>
              </div>

              <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 shadow-lg">
                <Radio className={`w-4 h-4 ${isAnalyzing ? 'text-yellow-400 animate-pulse' : 'text-green-400'}`} />
                <span className="text-xs font-bold tracking-wider uppercase text-white/90">
                    {isAnalyzing ? 'FETCHING...' : 'ONLINE'}
                </span>
              </div>
              <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 shadow-lg min-w-[140px]">
                <Timer className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-medium text-cyan-100">
                    Next Scan: <span className="font-bold text-white text-base ml-1">{timeLeft}s</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-10 pb-20">
        
        {prediction !== null && (
          <div className={`
            border-l-4 rounded-r-2xl p-6 mb-10 backdrop-blur-xl shadow-2xl transition-all duration-700 ease-in-out bg-black/50
            ${riskLevel === 'high' ? 'border-red-500' : riskLevel === 'moderate' ? 'border-yellow-500' : 'border-emerald-500'}
          `}>
            <div className="flex items-center gap-6">
              <div className={`p-4 rounded-full ${
                riskLevel === 'high' ? 'bg-red-500/20 text-red-400' :
                riskLevel === 'moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-emerald-500/20 text-emerald-400'
              }`}>
                <AlertTriangle className="w-8 h-8" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-2xl mb-1 text-white tracking-tight">
                  {riskLevel === 'high' ? 'CRITICAL ALERT: High Cloudburst Risk' : 
                   riskLevel === 'moderate' ? 'WARNING: Moderate Instability' : 
                   'STATUS: Weather Stable'}
                </h3>
                <p className="text-white/70 text-sm">
                  Automatic analysis based on latest telemetry.
                </p>
              </div>
              <div className="hidden md:block text-right">
                  <div className={`text-5xl font-black ${
                      riskLevel === 'high' ? 'text-red-400' : riskLevel === 'moderate' ? 'text-yellow-400' : 'text-emerald-400'
                  }`}>{prediction}%</div>
                  <div className="text-[10px] font-bold tracking-widest uppercase opacity-60">Probability</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            
            <GlassCard className="relative overflow-hidden">
                {isAnalyzing && (
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent animate-scan pointer-events-none z-20"></div>
                )}
                
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                        <Activity className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Live Sensor Feed</h2>
                        <div className="flex items-center gap-2 text-xs text-white/50 font-mono uppercase tracking-wide">
                             <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                             Stream Active
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2 bg-black/30 px-4 py-2 rounded-full border border-white/10 text-sm font-medium text-white/80">
                     <MapPin className="w-4 h-4 text-cyan-400" />
                     {location}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Temperature Card with Integrated 3D Thermometer */}
                <div className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:bg-white/10 transition-colors relative overflow-hidden group">
                  <div className="flex justify-between items-center h-full">
                      <div className="z-10">
                          <label className="flex items-center gap-2 text-sm font-semibold mb-3 text-orange-300">
                            <Thermometer className="w-4 h-4" /> Temperature
                          </label>
                          <div className="text-5xl font-light text-white mb-2 tracking-tighter">
                            {weatherData.temperature}<span className="text-2xl text-white/40 ml-1">°C</span>
                          </div>
                          <div className="text-xs text-white/40">RealFeel® {parseInt(weatherData.temperature) + 2}°</div>
                      </div>
                      <div className="z-10 pr-2">
                          <Thermometer3D temp={parseInt(weatherData.temperature)} />
                      </div>
                  </div>
                  <div className="absolute -right-6 -bottom-6 w-32 h-32 bg-red-600/10 rounded-full blur-3xl group-hover:bg-red-600/20 transition-all pointer-events-none"></div>
                </div>

                {/* Humidity Card with Integrated 3D Droplet + Condensation Effect */}
                <div className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:bg-white/10 transition-colors relative overflow-hidden group">
                  <CondensationBackground />
                  
                  <div className="flex justify-between items-center h-full relative z-10">
                      <div>
                          <label className="flex items-center gap-2 text-sm font-semibold mb-3 text-blue-300">
                            <Droplets className="w-4 h-4" /> Humidity
                          </label>
                          <div className="text-5xl font-light text-white mb-2 tracking-tighter">
                            {weatherData.humidity}<span className="text-2xl text-white/40 ml-1">%</span>
                          </div>
                          <div className="text-xs text-white/40">Dew Point {parseInt(weatherData.temperature) - 5}°</div>
                      </div>
                      <div className="pr-2">
                          <HumidityDroplet humidity={parseInt(weatherData.humidity)} />
                      </div>
                  </div>
                  <div className="absolute -right-6 -bottom-6 w-32 h-32 bg-blue-600/10 rounded-full blur-3xl group-hover:bg-blue-600/20 transition-all pointer-events-none"></div>
                </div>

                <div className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:bg-white/10 transition-colors">
                  <label className="flex items-center gap-2 text-sm font-semibold mb-2 text-purple-300">
                    <TrendingUp className="w-4 h-4" /> Pressure
                  </label>
                  <div className="text-4xl font-light text-white">
                    {weatherData.pressure}<span className="text-xl text-white/40 ml-1">hPa</span>
                  </div>
                </div>

                <div className="bg-white/5 rounded-2xl p-5 border border-white/5 hover:bg-white/10 transition-colors">
                  <label className="flex items-center gap-2 text-sm font-semibold mb-2 text-cyan-300">
                    <Wind className="w-4 h-4" /> Wind Speed
                  </label>
                  <div className="text-4xl font-light text-white">
                    {weatherData.windSpeed}<span className="text-xl text-white/40 ml-1">km/h</span>
                  </div>
                </div>

                <div className="md:col-span-2 bg-gradient-to-r from-blue-900/30 to-indigo-900/30 rounded-2xl p-5 border border-blue-500/20 relative overflow-hidden">
                  <div className="relative z-10 flex items-center justify-between">
                    <label className="flex items-center gap-2 text-sm font-semibold text-blue-300">
                        <CloudDrizzle className="w-4 h-4" /> Precipitation (1h)
                    </label>
                    <div className="text-4xl font-light text-white">
                        {weatherData.rainfall}<span className="text-xl text-white/40 ml-1">mm</span>
                    </div>
                  </div>
                  <div className="relative z-10 w-full h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden">
                      <div 
                        className="h-full bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.7)] transition-all duration-1000"
                        style={{ width: `${Math.min(parseFloat(weatherData.rainfall) * 2, 100)}%` }}
                      ></div>
                  </div>
                </div>
              </div>

              {/* NEW SINGLE COMBINED CHART SECTION */}
              <div className="mt-8 border-t border-white/10 pt-6">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-white/50 mb-6">Combined Trend Analysis</h3>
                  <div className="bg-white/5 rounded-2xl p-6 border border-white/5">
                      <MultiLineChart 
                        datasets={[
                            { label: 'Humidity (%)', data: history.humidity, color: '#60a5fa' },
                            { label: 'Pressure (hPa)', data: history.pressure, color: '#c084fc' },
                            { label: 'Wind (km/h)', data: history.wind, color: '#22d3ee' }
                        ]}
                        timestamps={history.timestamps}
                        className="h-full"
                      />
                  </div>
              </div>

              <div className="mt-8 pt-6 border-t border-white/10 flex justify-between text-[10px] text-white/30 font-mono uppercase tracking-widest">
                  <span>ID: #8392-AX</span>
                  <span>Latency: 12ms</span>
              </div>
            </GlassCard>

            {/* India Satellite Map Section */}
            <GlassCard className="p-0 overflow-hidden relative h-[350px] group">
                <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-10 bg-gradient-to-b from-black/80 to-transparent">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/10 backdrop-blur-md rounded-lg border border-white/10">
                            <Globe className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-sm">INSAT-3D Imagery</h3>
                            <div className="flex items-center gap-2 text-[10px] text-white/70 font-mono">
                                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                                LIVE FEED • SECTOR: INDIA
                            </div>
                        </div>
                    </div>
                    <div className="px-2 py-1 rounded bg-black/40 backdrop-blur-md border border-white/10 text-[10px] font-mono text-white/60">
                        IR-1 BAND
                    </div>
                </div>

                <div className="w-full h-full bg-slate-900 relative">
                    <img 
                        src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2000&auto=format&fit=crop" 
                        alt="Satellite Cloud Map" 
                        className="w-full h-full object-cover opacity-60 contrast-125 grayscale-[0.5]"
                    />
                    
                    <div className="absolute inset-0 origin-center animate-[spin_4s_linear_infinite] opacity-30 pointer-events-none">
                        <div className="w-full h-1/2 bg-gradient-to-b from-transparent to-cyan-500/20 border-b border-cyan-500/50"></div>
                    </div>

                    <div className="absolute inset-0 pointer-events-none p-4">
                        <div className="w-full h-full border-2 border-white/10 rounded-xl relative">
                            <div className="absolute top-1/4 left-1/4 w-3 h-3 border-l-2 border-t-2 border-cyan-500/80"></div>
                            <div className="absolute top-1/4 right-1/4 w-3 h-3 border-r-2 border-t-2 border-cyan-500/80"></div>
                            <div className="absolute bottom-1/4 left-1/4 w-3 h-3 border-l-2 border-b-2 border-cyan-500/80"></div>
                            <div className="absolute bottom-1/4 right-1/4 w-3 h-3 border-r-2 border-b-2 border-cyan-500/80"></div>
                            
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                                <Scan className="w-12 h-12 text-cyan-400/50 animate-pulse" strokeWidth={1} />
                            </div>
                        </div>
                    </div>
                </div>
            </GlassCard>

            {/* Satellite Data Table */}
            <GlassCard className="overflow-hidden">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <Database className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Satellite Telemetry</h2>
                  <div className="text-xs text-white/50 font-mono uppercase tracking-wide">Orbital Data Link</div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-[10px] text-cyan-200/50 border-b border-white/10 uppercase tracking-widest font-semibold">
                      <th className="py-4 px-3">Timestamp</th>
                      <th className="py-4 px-3">Lat / Lon</th>
                      <th className="py-4 px-3">CTT (℃)</th>
                      <th className="py-4 px-3">OT Index</th>
                      <th className="py-4 px-3">M-Flux</th>
                      <th className="py-4 px-3">CII</th>
                      <th className="py-4 px-3 text-right">Risk</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm font-mono text-white/80">
                    {satelliteData.map((row, idx) => (
                      <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="py-3 px-3 text-white/40">{row.timestamp}</td>
                        <td className="py-3 px-3">{row.lat}, {row.lon}</td>
                        <td className="py-3 px-3 font-bold text-white">{row.ctt}</td>
                        <td className="py-3 px-3 text-white/60">{row.otIndex}</td>
                        <td className="py-3 px-3 text-white/60">{row.moistureFlux}</td>
                        <td className="py-3 px-3 text-white/60">{row.cii}</td>
                        <td className="py-3 px-3 text-right">
                           <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide border ${
                             row.riskLevel === 'Extreme' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                             row.riskLevel === 'Moderate' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 
                             'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                           }`}>
                             {row.riskLevel}
                           </span>
                        </td>
                      </tr>
                    ))}
                    {satelliteData.length === 0 && (
                        <tr>
                            <td colSpan="7" className="py-12 text-center text-white/30 italic">Establishing uplink...</td>
                        </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </GlassCard>

            {/* Risk Parameter Reference */}
            <GlassCard>
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                        <Info className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Risk Parameters</h2>
                        <div className="text-xs text-white/50 font-mono uppercase tracking-wide">Critical Thresholds Explained</div>
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-blue-300 flex items-center gap-2"><Droplets size={16} /> Humidity</span>
                            <span className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-300 font-bold border border-red-500/20">&gt; 80%</span>
                        </div>
                        <p className="text-xs text-white/60 leading-relaxed">High saturation levels indicate critical moisture mass, a primary precursor for cloudburst events.</p>
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-purple-300 flex items-center gap-2"><TrendingUp size={16} /> Pressure</span>
                            <span className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-300 font-bold border border-red-500/20">&lt; 1000 hPa</span>
                        </div>
                        <p className="text-xs text-white/60 leading-relaxed">Rapid pressure drops signal strong updrafts capable of holding massive water volumes aloft.</p>
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-cyan-300 flex items-center gap-2"><Wind size={16} /> Wind Speed</span>
                            <span className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-300 font-bold border border-red-500/20">&gt; 40 km/h</span>
                        </div>
                        <p className="text-xs text-white/60 leading-relaxed">Gale-force winds enhance moisture convergence, feeding the storm system rapidly.</p>
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-indigo-300 flex items-center gap-2"><CloudDrizzle size={16} /> Rainfall</span>
                            <span className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-300 font-bold border border-red-500/20">&gt; 50 mm</span>
                        </div>
                        <p className="text-xs text-white/60 leading-relaxed">Sudden high-intensity precipitation confirms active cloudburst dynamics in the region.</p>
                    </div>
                </div>
            </GlassCard>
          </div>

          <div className="space-y-8">
            <GlassCard className="flex flex-col items-center justify-center relative overflow-hidden min-h-[220px] w-1/2 mx-auto">
                <div className={`absolute inset-0 bg-gradient-to-br ${getRiskGradient(riskLevel)} opacity-20 transition-all duration-1000`}></div>
                
                <h3 className="text-md font-bold mb-6 text-center z-10 text-white tracking-wide">Real-time Analysis</h3>
                
                <div className="relative mb-2 z-10 scale-110">
                    <LeafProgress value={prediction || 0} color={getRiskColorHex(riskLevel)} />
                </div>

                <div className="text-center z-10 mt-2">
                    <div className="text-xs font-bold opacity-80 uppercase tracking-[0.2em] text-white">Risk Probability</div>
                </div>
            </GlassCard>

            {/* Analysis Pipeline Card (Interactive) */}
            <GlassCard className="p-4">
                <h3 className="text-xs font-bold mb-3 uppercase tracking-widest text-white/40">Analysis Pipeline</h3>
                <div className="space-y-3">
                    <div 
                        onClick={toggleStage2}
                        className={`flex items-center justify-between cursor-pointer p-2 -mx-2 rounded-lg transition-colors group ${
                            stage2Active ? 'bg-white/5' : 'hover:bg-white/5'
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-blue-500/20 rounded-lg group-hover:bg-blue-500/30 transition-colors">
                                <Radio size={14} className="text-blue-400" />
                            </div>
                            <div>
                                <div className="text-xs font-bold text-white/80 group-hover:text-white">Stage 2</div>
                                <div className="text-[10px] text-white/40">Aerostat Deployment</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                            {stage2Active ? (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                                    <span className="text-[10px] font-mono text-blue-300">ACTIVE</span>
                                </>
                            ) : (
                                <button className="px-2 py-0.5 rounded bg-blue-500/20 hover:bg-blue-500/40 text-[10px] font-bold text-blue-300 transition-colors">
                                    ACTIVATE
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="h-px bg-white/5 w-full"></div>

                    <div 
                        onClick={toggleStage3}
                        className={`flex items-center justify-between cursor-pointer p-2 -mx-2 rounded-lg transition-colors group ${
                            stage3Active ? 'bg-white/5' : 'hover:bg-white/5'
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-purple-500/20 rounded-lg group-hover:bg-purple-500/30 transition-colors">
                                <Scan size={14} className="text-purple-400" />
                            </div>
                            <div>
                                <div className="text-xs font-bold text-white/80 group-hover:text-white">Stage 3</div>
                                <div className="text-[10px] text-white/40">Drone Deployment</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                            {stage3Active ? (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
                                    <span className="text-[10px] font-mono text-purple-300">ACTIVE</span>
                                </>
                            ) : (
                                <button className="px-2 py-0.5 rounded bg-purple-500/20 hover:bg-purple-500/40 text-[10px] font-bold text-purple-300 transition-colors">
                                    ACTIVATE
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </GlassCard>

            <div className="flex flex-row gap-4">
                <GlassCard className="flex-1">
                    <h3 className="text-xs font-bold mb-4 uppercase tracking-widest text-white/40">Thresholds</h3>
                    <div className="space-y-2 text-[10px] font-mono">
                        <div className="flex justify-between p-2 rounded bg-emerald-500/10 border border-emerald-400/20 text-emerald-300">
                            <span>LOW</span> <span>00-35%</span>
                        </div>
                        <div className="flex justify-between p-2 rounded bg-yellow-500/10 border border-yellow-400/20 text-yellow-300">
                            <span>MOD</span> <span>36-60%</span>
                        </div>
                        <div className="flex justify-between p-2 rounded bg-red-500/10 border border-red-400/20 text-red-300">
                            <span>HIGH</span> <span>&gt; 60%</span>
                        </div>
                    </div>
                </GlassCard>
                
                <GlassCard className="flex-1">
                    <h3 className="text-xs font-bold mb-4 uppercase tracking-widest text-white/40">Metrics Guide</h3>
                    <div className="space-y-3 text-xs text-white/60">
                        <div className="flex justify-between border-b border-white/5 pb-1">
                            <span className="text-cyan-200">CTT</span> <span>Cloud Top Temp</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                            <span className="text-cyan-200">OT Index</span> <span>Overshooting Top</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                            <span className="text-cyan-200">M-Flux</span> <span>Moisture Flux</span>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* Aerostat Deployment Section (Stage 2) */}
            <div id="stage-2" className="scroll-mt-32 transition-all duration-500">
                <GlassCard className={`relative overflow-hidden transition-all duration-500 ${!stage2Active ? 'opacity-60 grayscale' : ''}`}>
                    {/* Background Pattern */}
                    {stage2Active && (
                        <div className="absolute inset-0 bg-blue-900/10 pointer-events-none">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -mr-16 -mt-16"></div>
                        </div>
                    )}
                    
                    <div className="flex items-center gap-4 mb-6 relative z-10">
                        <div className={`p-3 rounded-xl border transition-colors ${stage2Active ? 'bg-blue-500/20 border-blue-500/30' : 'bg-white/5 border-white/10'}`}>
                            <Radio size={24} className={stage2Active ? "text-blue-400" : "text-white/30"} />
                        </div>
                        <div>
                            <h2 className={`text-2xl font-bold ${stage2Active ? 'text-white' : 'text-white/50'}`}>Aerostat Deployment</h2>
                            <div className="flex items-center gap-2 text-xs font-mono">
                                {stage2Active ? (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
                                        <span className="text-blue-200/70">SYSTEM ACTIVE • ALTITUDE: 850m</span>
                                    </>
                                ) : (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-red-500"></span>
                                        <span className="text-red-400/70">SYSTEM OFFLINE • AWAITING DEPLOYMENT</span>
                                    </>
                                )}
                            </div>
                        </div>
                        
                        {!stage2Active && (
                            <button 
                                onClick={toggleStage2}
                                className="ml-auto px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                            >
                                DEPLOY NOW
                            </button>
                        )}
                    </div>

                    {stage2Active ? (
                        <>
                            {/* Aerostat Animation */}
                            <Aerostat />
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
                                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-white/60">Tether Tension</span>
                                        <Anchor size={16} className="text-blue-400" />
                                    </div>
                                    <div className="text-2xl font-bold font-mono">4,250 <span className="text-sm text-white/40 font-sans">N</span></div>
                                    <div className="w-full bg-white/10 h-1.5 rounded-full mt-3 overflow-hidden">
                                        <div className="h-full bg-blue-500 w-3/4"></div>
                                    </div>
                                </div>

                                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-white/60">Coverage Radius</span>
                                        <Wifi size={16} className="text-green-400" />
                                    </div>
                                    <div className="text-2xl font-bold font-mono">12.5 <span className="text-sm text-white/40 font-sans">km</span></div>
                                    <div className="w-full bg-white/10 h-1.5 rounded-full mt-3 overflow-hidden">
                                        <div className="h-full bg-green-500 w-full"></div>
                                    </div>
                                </div>

                                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-white/60">Wind Shear</span>
                                        <Wind size={16} className="text-yellow-400" />
                                    </div>
                                    <div className="text-2xl font-bold font-mono">18 <span className="text-sm text-white/40 font-sans">km/h</span></div>
                                    <div className="w-full bg-white/10 h-1.5 rounded-full mt-3 overflow-hidden">
                                        <div className="h-full bg-yellow-500 w-1/3"></div>
                                    </div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-32 flex items-center justify-center border-t border-white/5 border-dashed">
                            <p className="text-white/30 text-sm italic">Aerostat telemetry unavailable. Please activate Stage 2.</p>
                        </div>
                    )}
                </GlassCard>
            </div>

            {/* Drone Fleet Section (Stage 3) */}
            <div id="stage-3" className="scroll-mt-32 transition-all duration-500">
                <GlassCard className={`relative overflow-hidden transition-all duration-500 ${!stage3Active ? 'opacity-60 grayscale' : ''}`}>
                    {/* Background Pattern */}
                    {stage3Active && (
                        <div className="absolute inset-0 bg-purple-900/10 pointer-events-none">
                            <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl -ml-16 -mb-16"></div>
                        </div>
                    )}

                    <div className="flex items-center gap-4 mb-6 relative z-10">
                        <div className={`p-3 rounded-xl border transition-colors ${stage3Active ? 'bg-purple-500/20 border-purple-500/30' : 'bg-white/5 border-white/10'}`}>
                            <Scan size={24} className={stage3Active ? "text-purple-400" : "text-white/30"} />
                        </div>
                        <div>
                            <h2 className={`text-2xl font-bold ${stage3Active ? 'text-white' : 'text-white/50'}`}>Drone Fleet Status</h2>
                            <div className="flex items-center gap-2 text-xs font-mono">
                                {stage3Active ? (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
                                        <span className="text-purple-200/70">SQUADRON ACTIVE • PATROLLING</span>
                                    </>
                                ) : (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-white/20"></span>
                                        <span className="text-white/40">SQUADRON STANDBY • AWAITING DEPLOYMENT</span>
                                    </>
                                )}
                            </div>
                        </div>

                        {!stage3Active && (
                            <button 
                                onClick={toggleStage3}
                                className="ml-auto px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-purple-500/20"
                            >
                                LAUNCH FLEET
                            </button>
                        )}
                    </div>

                    {stage3Active ? (
                        <>
                            {/* Drone Fleet Animation */}
                            <DroneFleet />
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
                                {[1, 2, 3, 4].map((id) => (
                                    <div key={id} className="bg-white/5 rounded-xl p-4 border border-white/5 hover:bg-white/10 transition-colors group">
                                        <div className="flex justify-between items-start mb-3">
                                            <div className="text-xs font-mono text-white/40">DRN-{id}0{id}</div>
                                            <div className={`px-2 py-0.5 rounded text-[10px] font-bold ${id === 1 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                                                {id === 1 ? 'RTH' : 'ACTIVE'}
                                            </div>
                                        </div>
                                        <div className="flex flex-col gap-2">
                                            <div className="flex items-center gap-2 text-xs text-white/70">
                                                <Battery size={12} className={id === 1 ? "text-yellow-400" : "text-green-400"} />
                                                <span>{id === 1 ? '15%' : '88%'}</span>
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-white/70">
                                                <Navigation size={12} className="text-purple-400" />
                                                <span>{id === 1 ? 'Base' : 'Sector 4'}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="h-32 flex items-center justify-center border-t border-white/5 border-dashed">
                            <p className="text-white/30 text-sm italic">Drone telemetry offline. Activate Stage 3 to view fleet status.</p>
                        </div>
                    )}
                </GlassCard>
            </div>

          </div>
        </div>
      </div>

      <style>{`
        @keyframes scan {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }
        .animate-scan {
            animation: scan 2s linear infinite;
        }
        @keyframes aerostat-deploy {
            0% { transform: translateY(200px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
        @keyframes aerostat-float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .animate-aerostat-deploy {
            animation: aerostat-deploy 8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        .animate-aerostat-float {
            animation: aerostat-float 8s ease-in-out infinite;
        }

        /* Drone Animation Keyframes - Start at bottom (0px offset from bottom) and move up to -240px */
        @keyframes drone-launch {
            0% { transform: translateY(100%) scale(0.5); opacity: 0; }
            60% { transform: translateY(-260px) scale(1.1); opacity: 1; }
            100% { transform: translateY(-240px) scale(1); opacity: 1; }
        }
        
        /* Hover animations relative to the launched position (-240px) */
        /* FIX: Change these to be relative to 0, since the parent container is already at -240px */
        @keyframes drone-hover-1 {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        @keyframes drone-hover-2 {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-12px); }
        }
        @keyframes drone-hover-3 {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes spin-fast {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Wrapper animation: Handles the launch sequence */
        .animate-drone-launch-1 { animation: drone-launch 2.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
        .animate-drone-launch-2 { animation: drone-launch 3s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards; }
        .animate-drone-launch-3 { animation: drone-launch 2.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.5s forwards; }
        
        /* Inner animation: Handles the hover bobbing */
        .animate-drone-hover-1 { animation: drone-hover-1 4s ease-in-out 2.5s infinite; }
        .animate-drone-hover-2 { animation: drone-hover-2 5s ease-in-out 3.2s infinite; }
        .animate-drone-hover-3 { animation: drone-hover-3 4.5s ease-in-out 3.3s infinite; }
        
        .animate-spin-fast { animation: spin-fast 0.1s linear infinite; }

      `}</style>
    </div>
  );
}