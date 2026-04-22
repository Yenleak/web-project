import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StatisticsService } from '../../Services/statistics';
import { Statistics } from '../../Models/statistics';

@Component({
  selector: 'app-statistics',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './statistics.html',
  styleUrl: './statistics.css'
})
export class StatisticsComponent implements OnInit {
  stats: Statistics | null = null;
  error = '';
  activeFilter: '1' | '3' | '7' | 'custom' = '1';
  customFrom = '';
  customTo = '';

  constructor(private statisticsService: StatisticsService) {}

  ngOnInit() {
    this.loadStats(1);
  }

  loadStats(days?: number) {
    this.statisticsService.getStatistics(days).subscribe({
      next: (data) => this.stats = data,
      error: () => this.error = 'Ошибка загрузки статистики'
    });
  }

  setFilter(filter: '1' | '3' | '7' | 'custom') {
    this.activeFilter = filter;
    if (filter !== 'custom') {
      this.loadStats(Number(filter));
    }
  }

  loadCustom() {
    if (!this.customFrom || !this.customTo) return;
    this.statisticsService.getStatistics(undefined, this.customFrom, this.customTo).subscribe({
      next: (data) => this.stats = data,
      error: () => this.error = 'Ошибка загрузки статистики'
    });
  }
}
