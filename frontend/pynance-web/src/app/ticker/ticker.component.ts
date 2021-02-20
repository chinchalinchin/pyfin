import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Console } from 'console';

// A component used to retrieve ticker symbols for app calculations.
// TODO: needs to emit the tickers being added.
@Component({
  selector: 'app-ticker',
  templateUrl: './ticker.component.html'
})
export class TickerComponent implements OnInit {

  @Output()
  private addTickers = new EventEmitter<string[]>();
  
  private inputTickers: string;
  private tickers : string[] = [];

  constructor() { }

  ngOnInit() {
  }

  public saveTickers(){
    let strippedTickers = this.inputTickers.replace(/\s/g, "");
    let parsedTickers : string[]= strippedTickers.split(',');
    for(let ticker of parsedTickers){ 
      this.tickers.push(ticker);
    }
    this.addTickers.emit(this.tickers);
    this.inputTickers = null;
  }

}
