import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Waves, CloudRain, Thermometer, Droplets, Wind, 
  Search, MapPin, RefreshCw, AlertTriangle, CheckCircle2,
  Calendar, Clock, Trash2
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = "/api";

const App = () => {
  const [city, setCity] = useState("Chennai");
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPrediction();
    fetchHistory();
  }, []);

  const fetchPrediction = async (searchCity = city) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get coords from Nominatim
      const geoRes = await axios.get(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(searchCity)}&format=json&limit=1`);
      
      let endpoint = `${API_BASE}/predict`;
      if (geoRes.data && geoRes.data.length > 0) {
        const { lat, lon } = geoRes.data[0];
        endpoint = `${API_BASE}/predict/${lat}/${lon}?location=${encodeURIComponent(searchCity)}`;
      }

      const res = await axios.get(endpoint);
      setPrediction(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch live prediction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history?limit=10`);
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const deleteHistory = async () => {
    if (!confirm("Are you sure you want to clear all history?")) return;
    try {
      await axios.delete(`${API_BASE}/history`);
      setHistory([]);
    } catch (err) {
      console.error(err);
    }
  };

  const chartData = prediction ? [
    { name: 'Rain', value: prediction.rainfall_mm, color: '#4fc3f7' },
    { name: 'River', value: prediction.river_level_m * 10, color: '#29b6f6' }, // Scaled
    { name: 'Hum', value: prediction.humidity_pct, color: '#0288d1' },
    { name: 'Temp', value: prediction.temperature_c, color: '#f48fb1' },
    { name: 'Wind', value: prediction.wind_speed_kmh, color: '#81c784' }
  ] : [];

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-[#cdd9e5] p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-center bg-slate-900/50 p-6 rounded-3xl border border-white/5 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-4 md:mb-0">
            <div className="p-3 bg-blue-500/20 rounded-2xl">
              <Waves className="text-blue-400 w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter">FLOODGUARD <span className="text-blue-400">OS</span></h1>
              <p className="text-xs text-slate-400 uppercase tracking-widest font-bold">Predictive Analytics Platform</p>
            </div>
          </div>

          <div className="flex gap-2 bg-slate-800/50 p-2 rounded-2xl border border-white/5 focus-within:border-blue-400/50 transition-all">
            <input 
              type="text" 
              value={city}
              onChange={(e) => setCity(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && fetchPrediction()}
              placeholder="Search Global Cities..."
              className="bg-transparent border-none outline-none px-4 py-2 w-full md:w-64 text-sm"
            />
            <button 
              onClick={() => fetchPrediction()}
              className="p-3 bg-blue-500 hover:bg-blue-600 rounded-xl text-slate-900 transition-colors"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Risk Status */}
          <section className="lg:col-span-4 space-y-8">
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div 
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="h-80 bg-slate-900/50 rounded-[40px] flex flex-col items-center justify-center border border-white/5"
                >
                  <RefreshCw className="w-12 h-12 text-blue-400 animate-spin" />
                  <p className="mt-4 text-slate-400 font-bold uppercase tracking-widest text-xs">Syncing Core Analytics...</p>
                </motion.div>
              ) : prediction && (
                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                  className={`h-80 rounded-[40px] p-8 flex flex-col items-center justify-center relative overflow-hidden border-2 
                    ${prediction.risk_level === 'HIGH' ? 'border-red-500/50' : 'border-emerald-500/50 shadow-[0_0_50px_rgba(16,185,129,0.1)]'}`}
                >
                  <div className={`absolute inset-0 opacity-10 animate-pulse 
                    ${prediction.risk_level === 'HIGH' ? 'bg-red-500' : 'bg-emerald-500'}`} 
                  />
                  
                  {prediction.risk_level === 'HIGH' ? (
                    <AlertTriangle className="w-20 h-20 text-red-500 mb-4" />
                  ) : (
                    <CheckCircle2 className="w-20 h-20 text-emerald-500 mb-4" />
                  )}
                  
                  <h2 className={`text-6xl font-black tracking-tighter ${prediction.risk_level === 'HIGH' ? 'text-red-500' : 'text-emerald-500'}`}>
                    {prediction.risk_level}
                  </h2>
                  <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mt-2">FLOOD RISK LEVEL</p>
                  <div className="mt-6 flex items-center gap-2 text-slate-500 bg-black/30 px-4 py-2 rounded-full border border-white/5">
                    <MapPin className="w-4 h-4" />
                    <span className="text-sm font-medium">{prediction.location}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              {prediction && [
                { icon: CloudRain, label: "Rainfall", val: prediction.rainfall_mm, unit: "mm" },
                { icon: Waves, label: "River Lvl", val: prediction.river_level_m.toFixed(2), unit: "m" },
                { icon: Thermometer, label: "Temp", val: prediction.temperature_c, unit: "°C" },
                { icon: Droplets, label: "Humidity", val: prediction.humidity_pct, unit: "%" }
              ].map((stat, i) => (
                <div key={i} className="bg-slate-900/40 p-4 rounded-3xl border border-white/5 flex flex-col items-center justify-center text-center">
                  <stat.icon className="w-5 h-5 text-blue-400 mb-2" />
                  <div className="text-xl font-black">{stat.val}<span className="text-[10px] text-slate-500 ml-1">{stat.unit}</span></div>
                  <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">{stat.label}</div>
                </div>
              ))}
            </div>
          </section>

          {/* Detailed Analytics */}
          <section className="lg:col-span-8 flex flex-col gap-8">
            
            {/* Chart Area */}
            <div className="flex-1 bg-slate-900/50 rounded-[40px] p-8 border border-white/5 min-h-[400px]">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h3 className="text-xl font-black text-white">ENVIRONMENTAL PROFILE</h3>
                  <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Live Sensor Data Vector</p>
                </div>
                {prediction && (
                  <div className="text-right">
                    <div className="text-blue-400 font-black text-2xl">{(prediction.risk_probability * 100).toFixed(1)}%</div>
                    <div className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Confidence Index</div>
                  </div>
                )}
              </div>
              
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis 
                      dataKey="name" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#64748b', fontSize: 10, fontWeight: 700 }}
                    />
                    <YAxis hide />
                    <Tooltip 
                      cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                      contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    />
                    <Bar dataKey="value" radius={[10, 10, 0, 0]} barSize={50} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Weather Summary Card */}
            {prediction && (
              <div className="bg-blue-600 p-8 rounded-[40px] flex items-center justify-between shadow-2xl shadow-blue-500/20">
                <div className="flex items-center gap-6">
                  <div className="p-5 bg-white/20 rounded-full backdrop-blur-md">
                    <Wind className="text-white w-10 h-10" />
                  </div>
                  <div>
                    <h4 className="text-white text-2xl font-black tracking-tight">{prediction.weather_desc}</h4>
                    <p className="text-blue-100 font-bold uppercase tracking-widest text-[10px] opacity-75">Atmospheric Condition</p>
                  </div>
                </div>
                <div className="text-right flex flex-col gap-1">
                  <div className="flex items-center justify-end gap-2 text-white/90">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm font-bold uppercase">{new Date(prediction.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div className="flex items-center justify-end gap-2 text-white/60">
                    <Calendar className="w-4 h-4" />
                    <span className="text-[10px] font-bold uppercase">{new Date(prediction.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* History */}
          <section className="lg:col-span-12">
            <div className="bg-slate-900/50 rounded-[40px] p-8 border border-white/5">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-black text-white tracking-tight">📜 PREDICTION LOG</h3>
                  <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Historical Data Stream</p>
                </div>
                <button 
                  onClick={deleteHistory}
                  className="p-3 text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded-2xl transition-all"
                  title="Clear All History"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-[10px] font-black uppercase text-slate-500 tracking-[0.2em] border-b border-white/5">
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap">Timestamp</th>
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap">Location</th>
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap text-center">Rain</th>
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap text-center">River</th>
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap text-center">Risk</th>
                      <th className="pb-4 pt-2 px-4 whitespace-nowrap text-center">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {history.map((rec, i) => (
                      <tr key={rec.id} className="border-b border-white/5 hover:bg-white/5 group transition-colors">
                        <td className="py-4 px-4 text-slate-400 font-medium">
                          {new Date(rec.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          <span className="ml-3 opacity-0 group-hover:opacity-100 text-[10px]">
                            {new Date(rec.timestamp).toLocaleDateString()}
                          </span>
                        </td>
                        <td className="py-4 px-4 font-bold text-slate-200">{rec.location}</td>
                        <td className="py-4 px-4 text-center font-bold text-blue-400/80">{rec.rainfall_mm}mm</td>
                        <td className="py-4 px-4 text-center font-bold text-blue-300/80">{rec.river_level_m}m</td>
                        <td className="py-4 px-4 text-center">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase 
                            ${rec.risk_level === 'HIGH' ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                            {rec.risk_level}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center font-black text-slate-400">{(rec.risk_probability * 100).toFixed(0)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

        </main>
        
        <footer className="text-center py-8">
            <p className="text-[10px] text-slate-700 font-black uppercase tracking-[0.4em]">FloodGuard OS &copy; 2026 // Real-time ML Intelligence</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
