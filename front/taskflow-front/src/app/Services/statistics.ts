import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Statistics } from '../Models/statistics';

@Injectable({ providedIn: 'root' })
export class StatisticsService {
  private api = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getStatistics(days?: number, from?: string, to?: string): Observable<Statistics> {
    let params = '';
    if (days) params = `?days=${days}`;
    else if (from && to) params = `?from=${from}&to=${to}`;
    return this.http.get<Statistics>(`${this.api}/statistics/${params}`);
  }
}
