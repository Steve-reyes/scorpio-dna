const API_BASE = import.meta.env.VITE_API_URL || '';

export interface Validation {
  total_snps: number;
  unique_snps: number;
  missing_genotypes: number;
}

export interface ReportResult {
  rsid: string;
  category: string;
  trait: string;
  description: string;
  genotype: string;
  risk_allele: string;
  risk_genotype: string;
  result: string;
  status_text: string;
  color: string;
  population_freq: number;
  study_url: string;
  note: string;
}

export interface ReportSummary {
  total_matched: number;
  categories: Record<string, { count: number; high_count: number }>;
  results: ReportResult[];
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  validation: Validation;
  report: ReportSummary;
  total_snps: number;
  matched_snps: number;
}

export async function uploadDna(file: File, password: string): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);
  form.append('password', password);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }

  return res.json();
}

export async function downloadPdf(file: File, password: string): Promise<Blob> {
  const form = new FormData();
  form.append('file', file);
  form.append('password', password);

  const res = await fetch(`${API_BASE}/api/report/pdf`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'PDF failed' }));
    throw new Error(err.detail || 'PDF generation failed');
  }

  return res.blob();
}

export function getCategoryColor(cat: string): string {
  const colors: Record<string, string> = {
    'Health': '#FF3B30',
    'Carrier': '#007AFF',
    'Drug Response': '#FF2D55',
    'Traits': '#AF52DE',
    'Nutrition': '#FF9500',
    'Fitness': '#34C759',
    'Personality': '#5856D6',
  };
  return colors[cat] || '#86868B';
}

export function getCategoryEmoji(cat: string): string {
  const icons: Record<string, string> = {
    'Health': '🩺',
    'Carrier': '🧬',
    'Drug Response': '💊',
    'Traits': '🧠',
    'Nutrition': '🥗',
    'Fitness': '🏃',
    'Personality': '🎭',
  };
  return icons[cat] || '📋';
}

export function getCategoryDescription(cat: string): string {
  const descs: Record<string, string> = {
    'Health': 'Chronic disease risk, wellness markers, metabolic health',
    'Carrier': 'Inherited condition carrier status screening',
    'Drug Response': 'How your body processes medications and supplements',
    'Traits': 'Physical characteristics: eye color, hair, skin, earwax',
    'Nutrition': 'How your genes affect nutrient metabolism and diet response',
    'Fitness': 'Athletic potential, recovery, injury risk',
    'Personality': 'Behavioral traits, mood regulation, taste perception',
  };
  return descs[cat] || '';
}
