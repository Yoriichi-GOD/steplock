/** Presentation-only choreography. Never accepts or returns inspection verdicts. */
export interface StoryPose {progress:number;lift:number;travel:number;turn:number;factory:number;isolation:number;deviation:number;light:number}
const keys:StoryPose[]=[
 {progress:0,lift:.25,travel:0,turn:-.2,factory:.55,isolation:0,deviation:0,light:.75},
 {progress:.18,lift:.5,travel:0,turn:0,factory:1,isolation:0,deviation:0,light:1},
 {progress:.3,lift:.75,travel:0,turn:.3,factory:1,isolation:0,deviation:1,light:1},
 {progress:.4,lift:.12,travel:0,turn:.45,factory:1,isolation:0,deviation:1,light:1},
 {progress:.57,lift:.12,travel:1,turn:.65,factory:1,isolation:0,deviation:1,light:1},
 {progress:.65,lift:.65,travel:.2,turn:.65,factory:0,isolation:1,deviation:1,light:.4},
 {progress:.73,lift:.65,travel:.2,turn:.65,factory:0,isolation:1,deviation:1,light:.4},
 {progress:.85,lift:.8,travel:0,turn:.1,factory:0,isolation:0,deviation:1,light:1.25},
 {progress:1,lift:0,travel:0,turn:0,factory:0,isolation:0,deviation:0,light:1.25}
];
export function storyPose(raw:number):StoryPose{
 const progress=Math.min(1,Math.max(0,Number.isFinite(raw)?raw:0));
 const next=keys.findIndex(key=>key.progress>=progress);if(next<=0)return {...keys[0],progress};
 const a=keys[next-1],b=keys[next],f=(progress-a.progress)/(b.progress-a.progress);
 const result={progress} as StoryPose;
 for(const name of ['lift','travel','turn','factory','isolation','deviation','light'] as const)result[name]=a[name]+(b[name]-a[name])*f;
 return result;
}
export const storyActs=['The factory','The knowledge gap','Late feedback','A different moment'];
export function storyAct(progress:number){return progress<.2?0:progress<.4?1:progress<.75?2:3}
