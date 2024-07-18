declare module 'baffle' {
    interface BaffleOptions {
      characters?: string;
      speed?: number;
    }
  
    interface BaffleInstance {
      start: () => BaffleInstance;
      stop: () => BaffleInstance;
      reveal: (duration: number) => BaffleInstance;
      set: (options: BaffleOptions) => BaffleInstance;
    }
  
    function baffle(selector: string | Element | NodeListOf<Element>, options?: BaffleOptions): BaffleInstance;
  
    export = baffle;
  }