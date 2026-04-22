import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = 'http://localhost:8000';

  constructor(private http: HttpClient, private router: Router) {}

  register(data: { name: string; email: string; password: string }): Observable<any> {
    return this.http.post(`${this.api}/register/`, data).pipe(
      tap((res: any) => this.saveTokens(res))
    );
  }

  login(data: { email: string; password: string }): Observable<any> {
    return this.http.post(`${this.api}/token/`, data).pipe(
      tap((res: any) => this.saveTokens(res))
    );
  }

  logout(): void {
    const refresh = localStorage.getItem('refresh');
    this.http.post(`${this.api}/logout/`, { refresh }).subscribe();
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    this.router.navigate(['/login']);
  }

  private saveTokens(res: any): void {
    localStorage.setItem('access', res.access);
    localStorage.setItem('refresh', res.refresh);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access');
  }
}
