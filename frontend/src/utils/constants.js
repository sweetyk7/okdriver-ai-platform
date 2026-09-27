export const DUMMY_VIDEOS = [
  'https://samplelib.com/lib/preview/mp4/sample-5s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-10s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-15s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-20s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-30s.mp4'
];

export function getDummyVideo(id) {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = id.charCodeAt(i) + ((hash << 5) - hash);
  return DUMMY_VIDEOS[Math.abs(hash) % DUMMY_VIDEOS.length];
}

export const LAYOUT_OPTIONS = [
  { label: '1×1', cols: 1 },
  { label: '2×2', cols: 2 },
  { label: '3×3', cols: 3 },
  { label: '4×4', cols: 4 },
];
