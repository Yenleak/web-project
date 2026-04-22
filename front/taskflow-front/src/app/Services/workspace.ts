import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Workspace } from '../Models/workspace';

@Injectable({ providedIn: 'root' })
export class WorkspaceService {
  private api = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getWorkspaces(): Observable<Workspace[]> {
    return this.http.get<Workspace[]>(`${this.api}/workspaces/`);
  }

  createWorkspace(data: { name: string; deadline?: string }): Observable<Workspace> {
    return this.http.post<Workspace>(`${this.api}/workspaces/`, data);
  }

  addMember(workspaceId: number, email: string): Observable<any> {
    return this.http.post(`${this.api}/workspaces/${workspaceId}/add-members/`, { email });
  }
}
