// 乐队类型定义
export interface Band {
  id: number;
  name: string;
  genre: string;
  image: string;
  year: number;
  member_count: number;
  banner_image_url: string;
  bio: string;
}

// 粒子类型定义
export interface Particle {
  size: number;
  top: number;
  left: number;
  duration: number;
  delay: number;
}