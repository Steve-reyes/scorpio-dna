import { useState, useRef, useCallback } from 'react';
import {
  uploadDna, downloadPdf,
  type UploadResponse, type ReportResult,
  getCategoryColor, getCategoryEmoji, getCategoryDescription
} from './lib/api';

type Page = 'login' | 'upload' | 'loading' | 'dashboard' | 'category' | 'detail' | 'filtered';

const CATEGORY_ORDER = ['Health', 'Carrier', 'Drug Response', 'Traits', 'Nutrition', 'Fitness', 'Personality', 'Ancestry', 'Ethnicity'];

const TRAIT_ICONS: Record<string, string> = {
  'Obesity / BMI': '⚖️',
  'MTHFR Deficiency': '🧪',
  "Alzheimer's Risk (APOE)": '🧠',
  'Hemochromatosis (HFE)': '🩸',
  'Lipoprotein(a) / Heart Disease': '❤️',
  'Triglycerides': '🫧',
  'Type 2 Diabetes': '🩸',
  'TNF-alpha / Inflammation': '🔥',
  'IL-1B / Inflammation': '🔥',
  'IL-6 / Inflammation': '🔥',
  'MTHFR A1298C': '🧪',
  'Asthma / ADRB2': '🫁',
  'Nicotine Dependence': '🚬',
  'Vitamin D / Osteoporosis': '☀️',
  'Vitamin D / Autoimmunity': '☀️',
  'Lactose Intolerance': '🥛',
  'NAFLD / Fatty Liver': '🫁',
  "NAFLD / Liver Disease": '🫁',
  "Crohn's Disease / NOD2": '🫀',
  'Autoimmunity / TYK2': '🛡️',
  'Coronary Artery Disease': '❤️',
  'Heart Attack / CAD': '❤️',
  'Heart Disease / LPL': '❤️',
  'Serotonin / Mood': '🧠',
  'Serotonin / Depression': '🧠',
  'COMT / Stress Response': '🧠',
  'BDNF / Memory & Mood': '🧠',
  'ACTN3 / Muscle Performance': '💪',
  'Sickle Cell Anemia': '🩸',
  'Factor V Leiden': '🩸',
  'Prothrombin / Clotting': '🩸',
  'Cystic Fibrosis (ΔF508)': '🫁',
  'Cystic Fibrosis (G551D)': '🫁',
  'Cystic Fibrosis (W1282X)': '🫁',
  'Tay-Sachs (HEXA)': '🧬',
  'G6PD Deficiency': '🩸',
  'BRCA1 / Breast Cancer': '🎗️',
  'BRCA2 / Breast Cancer': '🎗️',
  'Maple Syrup Urine Disease': '🧬',
  'Spinal Muscular Atrophy': '🧬',
  'Wilson Disease': '🫁',
  'Gaucher Disease': '🧬',
  'Warfarin Sensitivity': '💊',
  'Codeine Efficacy (CYP2D6)': '💊',
  'Tamoxifen Metabolism': '💊',
  'CYP2D6 / Drug Metabolism': '💊',
  'GSTP1 / Chemotherapy': '💊',
  'TP53 / Chemotherapy': '💊',
  'TPMT / Azathioprine': '💊',
  'TPMT / Thiopurines': '💊',
  'AHR / Detoxification': '🧪',
  'Caffeine Metabolism (CYP1A2)': '☕',
  'CYP3A5 / Drug Metabolism': '💊',
  'Statins / SLCO1B1': '💊',
  'CYP2C19 / Clopidogrel': '💊',
  'Eye Color': '👁️',
  'Eye Color (Blue/Brown)': '👁️',
  'Hair Color (Red)': '🧑‍🦰',
  'Earwax Type': '👂',
  'Hair Thickness': '💇',
  'Skin Pigmentation': '🧴',
  'Lactose Tolerance': '🥛',
  'Freckles': '🟤',
  'Male Pattern Baldness': '👨‍🦲',
  'Hair Type (Straight/Curly)': '💇‍♂️',
  'Hair Graying': '👨‍🦳',
  'Folate Metabolism': '🥬',
  'Caffeine Metabolism': '☕',
  'Vitamin B12 Levels': '🥩',
  'Vitamin A / Iron': '🥩',
  'Iron Status': '🩸',
  'Vitamin B12 Status': '🥩',
  'Vitamin D Metabolism': '☀️',
  'Saturated Fat Sensitivity': '🧈',
  'Fatty Acid Metabolism': '🫒',
  'Omega-3 / Omega-6 Balance': '🐟',
  'Sodium Sensitivity': '🧂',
  'Salt / Blood Pressure': '🧂',
  'ACE / Blood Pressure': '❤️',
  'ACTN3 / Sprint Performance': '🏃',
  'Aerobic Fitness / PPARGC1A': '🏃',
  'PPARA / Endurance': '🏃',
  'IL-6 / Recovery': '💪',
  'ACE / Endurance vs Power': '🏃',
  'Muscle Mass / MSTN': '💪',
  'VO2 Max / VEGFR2': '🫁',
  'Lactate / MCT1': '🏃',
  'Injury Risk / COL5A1': '🤕',
  'Tendon Injury / COL5A1': '🤕',
  'COMT / Worrier vs Warrior': '🧠',
  'Anxiety / HTR2A': '🧠',
  'SERT / Stress Sensitivity': '🧠',
  'BDNF / Neuroticism': '🧠',
  'HTR2A / Personality': '🧠',
  'DRD2 / Reward Seeking': '🎯',
  'DBH / Norepinephrine': '🧠',
  'OXTR / Empathy & Social': '🤝',
  'GNB3 / Mood': '🧠',
  'TAS2R38 / Bitter Taste': '👅',
  'Lactate / MCT1': '🏃',
  // Ancestry / Haplogroups
  'K (maternal)': '🧬',
  'U (maternal)': '🧬',
  'T (maternal)': '🧬',
  'J (maternal)': '🧬',
  'J/T (maternal)': '🧬',
  'B (maternal)': '🧬',
  'L3 (maternal)': '🧬',
  'W (maternal)': '🧬',
  'HV (maternal)': '🧬',
  'T/X (maternal)': '🧬',
  'C (maternal)': '🧬',
  'D (maternal)': '🧬',
  'A (maternal)': '🧬',
  'A (paternal)': '🧬',
  'B (paternal)': '🧬',
  'C (paternal)': '🧬',
  'D (paternal)': '🧬',
  'E (paternal)': '🧬',
  'F (paternal)': '🧬',
  'G (paternal)': '🧬',
  'I (paternal)': '🧬',
  'I1 (paternal)': '🧬',
  'J (paternal)': '🧬',
  'J1 (paternal)': '🧬',
  'J2 (paternal)': '🧬',
  'K (paternal)': '🧬',
  'N (paternal)': '🧬',
  'O (paternal)': '🧬',
  'P (paternal)': '🧬',
  'Q (paternal)': '🧬',
  'R (paternal)': '🧬',
  'R1a (paternal)': '🧬',
  'R1b (paternal)': '🧬',
  'T (paternal)': '🧬',
};

function getTraitIcon(trait: string): string {
  return TRAIT_ICONS[trait] || '🧬';
}

function getResultPosition(result: string): number {
  const positions: Record<string, number> = { 'typical': 15, 'elevated': 50, 'high': 85, 'carrier': 50 };
  return positions[result] || 50;
}

function RiskMeter({ result }: { result: string }) {
  const pos = getResultPosition(result);
  return (
    <div className="risk-meter">
      <div className="risk-marker" style={{ left: `${pos}%` }} />
    </div>
  );
}

function App() {
  const [page, setPage] = useState<Page>('upload');
  const [password, setPassword] = useState('');
  const [passError, setPassError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [data, setData] = useState<UploadResponse | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<ReportResult | null>(null);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [filterLabel, setFilterLabel] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleLogin = () => {
    if (!password) { setPassError('Enter password'); return; }
    setPage('upload');
    setPassError('');
  };

  const handleUpload = useCallback(async (file: File) => {
    setUploading(true);
    setPage('loading');
    try {
      const result = await uploadDna(file, password);
      setData(result);
      setPage('dashboard');
    } catch (e: any) {
      setUploading(false);
      setPage('upload');
      alert(e.message || 'Upload failed — try a different file');
    }
  }, [password]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }, [handleUpload]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const handlePdfDownload = async () => {
    if (!data) return;
    const fileInput = fileInputRef.current;
    if (!fileInput?.files?.[0]) {
      alert('Please re-select your DNA file for PDF generation');
      return;
    }
    try {
      const blob = await downloadPdf(fileInput.files[0], password);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'scorpio-dna-report.pdf';
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      alert(e.message || 'PDF generation failed');
    }
  };

  const categoryResults = (cat: string) =>
    data?.report.results.filter(r => r.category === cat) || [];

  // ============ LOGIN ============
  if (page === 'login') {
    return (
      <div className="app-container">
        <div className="login-form">
          <div className="login-logo">🦂</div>
          <div className="login-title">Scorpio DNA</div>
          <div className="login-sub">Upload your raw DNA data and discover what your genes say about your health, traits, and more</div>
          <input className="input login-input" type="password" placeholder="Enter password" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleLogin()} />
          <button className="btn btn-primary login-btn" onClick={handleLogin}>Get Started</button>
          {passError && <div className="login-error">{passError}</div>}
        </div>
      </div>
    );
  }

  // ============ UPLOAD ============
  if (page === 'upload') {
    return (
      <div className="app-container">
        <div className="header">
          <div className="header-left">
            <div className="header-logo">🦂</div>
            <div>
              <div className="header-title">Scorpio DNA</div>
              <div className="header-subtitle">Raw DNA Analysis</div>
            </div>
          </div>
          <button className="btn btn-outline" onClick={() => setPage('login')}>Sign Out</button>
        </div>

        <div className="disclaimer">
          <strong>⚠ For Educational Purposes Only</strong> — This tool is not FDA-approved, not diagnostic, and not medical advice. Results are based on publicly available GWAS data. Always consult a healthcare professional.
        </div>

        <div className="category-preview">
          {[
            ['Health', '🩺', '#FF3B30'],
            ['Carrier', '🧬', '#007AFF'],
            ['Drug Response', '💊', '#FF2D55'],
            ['Traits', '🧠', '#AF52DE'],
            ['Nutrition', '🥗', '#FF9500'],
            ['Fitness', '🏃', '#34C759'],
            ['Personality', '🎭', '#5856D6'],
            ['Ancestry', '🗺️', '#8E8E93'],
            ['Ethnicity', '🌍', '#00BFA5'],
          ].map(([name, emoji, color]) => (
            <div key={name as string} className="preview-chip">
              <span>{emoji as string}</span>
              <span style={{ color: color as string }}>{name as string}</span>
            </div>
          ))}
        </div>

        <div
          className={`upload-zone ${dragOver ? 'dragging' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-icon">🧬</div>
          <div className="upload-title">Upload your raw DNA data</div>
          <div className="upload-subtitle">Drag & drop your 23andMe, AncestryDNA, or MyHeritage file here, or click to browse</div>
          <div className="file-badges">
            <span className="file-badge">23andMe</span>
            <span className="file-badge">AncestryDNA</span>
            <span className="file-badge">MyHeritage</span>
            <span className="file-badge">.txt / .zip</span>
          </div>
          <input ref={fileInputRef} type="file" accept=".txt,.csv,.tsv,.zip" onChange={handleFileSelect} style={{ display: 'none' }} />
        </div>

        {uploading && (
          <div className="loading-container">
            <div className="spinner" />
            <div className="loading-text">Analyzing your genome...</div>
            <div className="loading-sub">Scanning 600,000+ SNPs against 150+ health, trait, and ancestry markers</div>
          </div>
        )}
      </div>
    );
  }

  // ============ LOADING ============
  if (page === 'loading') {
    return (
      <div className="app-container">
        <div className="loading-container">
          <div className="spinner" />
          <div className="loading-text">Analyzing your DNA...</div>
          {data && (
            <div className="loading-sub">
              {data.total_snps?.toLocaleString()} SNPs scanned &middot; {data.report.total_matched} conditions matched
            </div>
          )}
        </div>
      </div>
    );
  }

  // ============ DASHBOARD ============
  if (page === 'dashboard' && data) {
    const report = data.report;
    const resultsByCat = CATEGORY_ORDER.map(c => ({
      category: c,
      count: report.categories[c]?.count || 0,
      high: report.categories[c]?.high_count || 0,
    }));

    return (
      <div className="app-container">
        <div className="header">
          <div className="header-left">
            <div className="header-logo">🦂</div>
            <div>
              <div className="header-title">Your DNA Report</div>
              <div className="header-subtitle">{data.filename} &middot; {data.total_snps?.toLocaleString()} SNPs &middot; {report.total_matched} matches</div>
            </div>
          </div>
          <input ref={fileInputRef} type="file" accept=".txt,.csv,.tsv,.zip" onChange={handleFileSelect} style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-outline" onClick={() => fileInputRef.current?.click()} style={{ fontSize: 12, padding: '6px 12px' }}>New Upload</button>
            <button className="btn btn-outline" onClick={handlePdfDownload} style={{ fontSize: 12, padding: '6px 12px' }}>Download PDF</button>
          </div>
        </div>

        <div className="disclaimer">
          <strong>⚠ For Educational Purposes Only</strong> — Not medical advice. Consult a professional.
        </div>

        <div className="summary-bar">
          <div className="summary-stat clickable" onClick={() => { setActiveFilter(null); setFilterLabel('All Conditions'); setPage('filtered'); }}>
            <div className="summary-num" style={{ color: '#5856D6' }}>{report.total_matched}</div>
            <div className="summary-label">Conditions Analyzed</div>
          </div>
          <div className="summary-stat clickable" onClick={() => { setActiveFilter('high'); setFilterLabel('Higher Risk'); setPage('filtered'); }}>
            <div className="summary-num" style={{ color: '#FF3B30' }}>{report.results.filter(r => r.result === 'high').length}</div>
            <div className="summary-label">Higher Risk</div>
          </div>
          <div className="summary-stat clickable" onClick={() => { setActiveFilter('elevated'); setFilterLabel('Elevated'); setPage('filtered'); }}>
            <div className="summary-num" style={{ color: '#FF9500' }}>{report.results.filter(r => r.result === 'elevated').length}</div>
            <div className="summary-label">Elevated</div>
          </div>
          <div className="summary-stat clickable" onClick={() => { setActiveFilter('carrier'); setFilterLabel('Carrier'); setPage('filtered'); }}>
            <div className="summary-num" style={{ color: '#007AFF' }}>{report.results.filter(r => r.result === 'carrier').length}</div>
            <div className="summary-label">Carrier</div>
          </div>
          <div className="summary-stat clickable" onClick={() => { setActiveFilter('typical'); setFilterLabel('Typical'); setPage('filtered'); }}>
            <div className="summary-num" style={{ color: '#34C759' }}>{report.results.filter(r => r.result === 'typical').length}</div>
            <div className="summary-label">Typical</div>
          </div>
        </div>

        <div className="category-grid">
          {resultsByCat.map(({ category, count, high }) => {
            if (category === 'Ethnicity') {
              const hasAdmixture = data.admixture && Object.keys(data.admixture).length > 0;
              const popCount = hasAdmixture ? Object.keys(data.admixture!).length : 0;
              return (
                <div key={category} className={`card card-clickable category-tile${!hasAdmixture ? ' category-empty' : ''}`} onClick={() => { setSelectedCategory(category); setPage('category'); }}>
                  <div className="category-icon" style={{ background: `#00BFA515` }}>
                    <span>🌍</span>
                  </div>
                  <div className="category-info">
                    <div className="category-name" style={{ color: '#00BFA5' }}>Ethnicity</div>
                    <div className="category-count">{hasAdmixture ? `${popCount} populations estimated` : 'No data'}</div>
                    <div className="category-desc">Autosomal admixture estimate based on 50+ ancestry-informative markers</div>
                  </div>
                </div>
              );
            }
            return (
            <div key={category} className={`card card-clickable category-tile${count === 0 ? ' category-empty' : ''}`} onClick={() => { setSelectedCategory(category); setPage('category'); }}>
              <div className="category-icon" style={{ background: `${getCategoryColor(category)}15` }}>
                <span>{getCategoryEmoji(category)}</span>
              </div>
              <div className="category-info">
                <div className="category-name" style={{ color: getCategoryColor(category) }}>{category}</div>
                <div className="category-count">{count} conditions {high > 0 ? `· ${high} flagged` : ''}</div>
                <div className="category-desc">{getCategoryDescription(category)}</div>
              </div>
            </div>
            );
          })}
        </div>
      </div>
    );
  }

  // ============ FILTERED RESULTS ============
  if (page === 'filtered' && data) {
    const filtered = activeFilter
      ? data.report.results.filter(r => r.result === activeFilter)
      : data.report.results;
    const resultColor = activeFilter === 'high' ? '#FF3B30' :
      activeFilter === 'elevated' ? '#FF9500' :
      activeFilter === 'carrier' ? '#007AFF' :
      activeFilter === 'typical' ? '#34C759' :
      '#5856D6';

    return (
      <div className="app-container">
        <button className="back-btn" onClick={() => setPage('dashboard')}>← Back to Dashboard</button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: `${resultColor}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>
            {activeFilter === 'high' ? '🔴' : activeFilter === 'elevated' ? '🟠' : activeFilter === 'carrier' ? '🔵' : activeFilter === 'typical' ? '🟢' : '🔮'}
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{filterLabel}</div>
            <div style={{ fontSize: 13, color: '#86868B' }}>{filtered.length} conditions</div>
          </div>
        </div>

        {filtered.map((r, i) => (
          <div key={i} className="card card-clickable condition-card" onClick={() => { setSelectedDetail(r); setPage('detail'); }}>
            <div className="condition-icon" style={{ background: `${getCategoryColor(r.category)}15` }}>
              <span>{getTraitIcon(r.trait)}</span>
            </div>
            <div className="condition-body">
              <div className="condition-header">
                <div className="condition-name">{r.trait}</div>
                <span className={`badge badge-${r.result}`}>
                  <span className="badge-dot" style={{ background: r.result === 'high' ? 'white' : '' }} />
                  {r.status_text}
                </span>
              </div>
              <div className="condition-desc">{r.description.slice(0, 150)}{r.description.length > 150 ? '...' : ''}</div>
              {r.summary && (
                <div className="summary-text">{r.summary.slice(0, 200)}{r.summary.length > 200 ? '...' : ''}</div>
              )}
              <RiskMeter result={r.result} />
              <div className="condition-meta">
                <span>Genotype: <strong>{r.genotype}</strong></span>
                <span>Risk Allele: <strong>{r.risk_allele}</strong></span>
                <span>Population: <strong>{(r.population_freq * 100).toFixed(0)}%</strong></span>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // ============ CATEGORY DETAIL ============
  if (page === 'category' && selectedCategory && data) {
    const results = categoryResults(selectedCategory);

    // Special rendering for Ethnicity (admixture)
    if (selectedCategory === 'Ethnicity' && data.admixture) {
      const admixture = data.admixture;
      const admixtureEntries = Object.entries(admixture)
        .sort(([, a], [, b]) => b - a);
      const regionConfig: Record<string, { color: string; flag: string }> = {
        'African': { color: '#E63946', flag: '🦒' },
        'European': { color: '#457B9D', flag: '🏰' },
        'East Asian': { color: '#E9C46A', flag: '🏮' },
        'South Asian': { color: '#F4A261', flag: '🕌' },
        'Native American': { color: '#2A9D8F', flag: '🏹' },
      };

      return (
        <div className="app-container">
          <button className="back-btn" onClick={() => setPage('dashboard')}>← Back to Dashboard</button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
            <div style={{ width: 48, height: 48, borderRadius: 14, background: 'linear-gradient(135deg, #00BFA5, #00897B)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>
              🌍
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#FFFFFF' }}>Ethnicity Estimate</div>
              <div style={{ fontSize: 13, color: '#A0A0A8' }}>Genetic admixture across {Object.keys(admixture).length} continental populations</div>
            </div>
          </div>

          <div className="card" style={{ padding: 20, marginBottom: 16, background: '#1C1C1E', border: '1px solid #38383A', borderRadius: 16 }}>
            {admixtureEntries.map(([region, pct], i) => {
              const barWidth = Math.max(pct * 100, 2);
              const config = regionConfig[region] || { color: '#00BFA5', flag: '🌍' };
              const isFirst = i === 0;
              return (
                <div key={region} style={{ marginBottom: i < admixtureEntries.length - 1 ? 18 : 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 18, marginRight: 10 }}>{config.flag}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>{region}</span>
                        <span style={{ fontSize: 18, fontWeight: 700, color: config.color }}>{(pct * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  <div style={{ height: 10, background: '#2C2C2E', borderRadius: 5, overflow: 'hidden', marginLeft: 34 }}>
                    <div style={{ height: '100%', width: `${barWidth}%`, background: `linear-gradient(90deg, ${config.color}, ${config.color}CC)`, borderRadius: 5, transition: 'width 0.6s ease' }} />
                  </div>
                  {isFirst && admixtureEntries.length > 1 && (
                    <div style={{ fontSize: 12, color: '#A0A0A8', marginTop: 4, marginLeft: 34 }}>
                      Largest component — {admixtureEntries[0][1] > 0.5 ? 'predominant' : 'plurality'} ancestry
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="card" style={{ padding: 20, background: '#1C1C1E', border: '1px solid #38383A', borderRadius: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#FFFFFF', marginBottom: 8 }}>How It Works</div>
            <div style={{ fontSize: 13, color: '#C0C0C8', lineHeight: 1.7 }}>
              Compares your DNA at <strong style={{ color: '#FFFFFF' }}>55 ancestry-informative markers (AIMs)</strong> against reference frequencies from five continental populations. Your genotype at each marker is scored using a log-likelihood model under Hardy-Weinberg equilibrium.
            </div>
            <div style={{ fontSize: 12, color: '#86868B', marginTop: 12, borderTop: '1px solid #2C2C2E', paddingTop: 12 }}>
              For educational purposes only. Not a substitute for commercial ancestry testing.
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="app-container">
        <button className="back-btn" onClick={() => setPage('dashboard')}>← Back to Dashboard</button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div className="category-icon" style={{ background: `${getCategoryColor(selectedCategory)}15`, width: 44, height: 44, fontSize: 20 }}>
            {getCategoryEmoji(selectedCategory)}
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{selectedCategory}</div>
            <div style={{ fontSize: 13, color: '#86868B' }}>{results.length} conditions found</div>
          </div>
        </div>

        {results.length > 0 ? results.map((r, i) => (
          <div key={i} className="card card-clickable condition-card" onClick={() => { setSelectedDetail(r); setPage('detail'); }}>
            <div className="condition-icon" style={{ background: `${getCategoryColor(selectedCategory)}15` }}>
              <span>{getTraitIcon(r.trait)}</span>
            </div>
            <div className="condition-body">
              <div className="condition-header">
                <div className="condition-name">{r.trait}</div>
                <span className={`badge badge-${r.result}`}>
                  <span className="badge-dot" style={{ background: r.result === 'high' ? 'white' : '' }} />
                  {r.status_text}
                </span>
              </div>
              <div className="condition-desc">{r.description.slice(0, 150)}{r.description.length > 150 ? '...' : ''}</div>
              {r.summary && (
                <div className="summary-text">{r.summary.slice(0, 200)}{r.summary.length > 200 ? '...' : ''}</div>
              )}
              <RiskMeter result={r.result} />
              <div className="condition-meta">
                <span>Genotype: <strong>{r.genotype}</strong></span>
                <span>Risk Allele: <strong>{r.risk_allele}</strong></span>
                <span>Population: <strong>{(r.population_freq * 100).toFixed(0)}%</strong></span>
              </div>
            </div>
          </div>
        )) : (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>{getCategoryEmoji(selectedCategory)}</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: '#86868B' }}>No markers detected in this category</div>
            <div style={{ fontSize: 13, color: '#86868B', marginTop: 8, lineHeight: 1.5 }}>
              Your DNA file may not contain the specific SNPs needed for this category.
              Try uploading a file from 23andMe or AncestryDNA for broader coverage.
            </div>
          </div>
        )}
      </div>
    );
  }

  // ============ CONDITION DETAIL ============
  if (page === 'detail' && selectedDetail && data) {
    const r = selectedDetail;
    return (
      <div className="app-container">
        <button className="back-btn" onClick={() => { setPage(activeFilter ? 'filtered' : 'category'); }}>← Back to {activeFilter ? filterLabel : selectedCategory}</button>

        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
            <div className="condition-icon" style={{ background: `${getCategoryColor(r.category)}15`, width: 56, height: 56, fontSize: 28 }}>
              {getTraitIcon(r.trait)}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: 20, fontWeight: 700 }}>{r.trait}</div>
                  <div style={{ fontSize: 13, color: getCategoryColor(r.category), fontWeight: 600, marginTop: 2 }}>{r.category}</div>
                </div>
                <span className={`badge badge-${r.result}`} style={{ fontSize: 13, padding: '5px 14px' }}>
                  {r.status_text}
                </span>
              </div>
            </div>
          </div>

          <RiskMeter result={r.result} />

          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 4 }}>About this trait</div>
            <div style={{ fontSize: 14, lineHeight: 1.6 }}>{r.description}</div>
          </div>

          {r.summary && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 4 }}>What this means for you</div>
              <div style={{ fontSize: 14, lineHeight: 1.6, color: '#333' }}>{r.summary}</div>
            </div>
          )}

          {r.health_tips && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#5856D6', textTransform: 'uppercase', marginBottom: 4 }}>Health Tips</div>
              <div style={{ fontSize: 14, lineHeight: 1.7, color: '#333', whiteSpace: 'pre-wrap' }}>{r.health_tips}</div>
            </div>
          )}

          {r.risk_factors && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#FF3B30', textTransform: 'uppercase', marginBottom: 4 }}>Risk Factors</div>
              <div style={{ fontSize: 14, lineHeight: 1.7, color: '#555', whiteSpace: 'pre-wrap' }}>{r.risk_factors}</div>
            </div>
          )}

          {r.if_untreated && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#8E8E93', textTransform: 'uppercase', marginBottom: 4 }}>If Not Managed</div>
              <div style={{ fontSize: 14, lineHeight: 1.6, color: '#666', background: '#F9F9FB', borderRadius: 8, padding: 12 }}>{r.if_untreated}</div>
            </div>
          )}

          <div style={{ marginTop: 20, display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 2 }}>Your Genotype</div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{r.genotype}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 2 }}>Risk Allele</div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{r.risk_allele}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 2 }}>Population Frequency</div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{(r.population_freq * 100).toFixed(0)}%</div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#86868B', textTransform: 'uppercase', marginBottom: 2 }}>dbSNP</div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{r.rsid}</div>
            </div>
          </div>

          {r.study_url && (
            <div style={{ marginTop: 20 }}>
              <a href={r.study_url} target="_blank" rel="noopener noreferrer" style={{ color: '#5856D6', fontSize: 14, fontWeight: 600 }}>View Study →</a>
            </div>
          )}

          {r.note && (
            <div style={{ marginTop: 16, background: '#F5F5F7', borderRadius: 8, padding: 10, fontSize: 12, color: '#86868B' }}>
              {r.note}
            </div>
          )}
        </div>
      </div>
    );
  }

  return null;
}

export default App;
