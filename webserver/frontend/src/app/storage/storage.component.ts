import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { ChartData, ChartOptions } from 'chart.js';

@Component({
  selector: 'hc-storage',
  templateUrl: './storage.component.html',
  styleUrls: ['./storage.component.scss']
})
export class StorageComponent implements OnInit, OnChanges {

  @Input() free: number = 0;
  @Input() used: number = 0;


  public pdata: ChartData = {
    labels: ["Free", "Used"],
    datasets: [
      {
        data: [0, 0],
        backgroundColor: ["#82b0d2", "#1d6da0"]
      },
    ]
  }

  public chartJsOptions: ChartOptions  = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        align: 'center',
      },
    }
    
  }

  constructor() { }

  ngOnInit(): void {
  }

  ngOnChanges(): void{
    this.pdata.datasets[0].data = [this.free, this.used];
  }
}
