import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, Subtask } from '../Models/task';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private api = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getTasks(workspaceId?: number): Observable<Task[]> {
    const params = workspaceId ? `?workspace=${workspaceId}` : '';
    return this.http.get<Task[]>(`${this.api}/tasks/${params}`);
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.api}/tasks/${id}/`);
  }

  createTask(data: Partial<Task>): Observable<Task> {
    return this.http.post<Task>(`${this.api}/tasks/`, data);
  }

  updateTask(id: number, data: Partial<Task>): Observable<Task> {
    return this.http.patch<Task>(`${this.api}/tasks/${id}/`, data);
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.api}/tasks/${id}/`);
  }

  toggleTask(id: number): Observable<any> {
    return this.http.patch(`${this.api}/tasks/${id}/toggle/`, {});
  }

  // Subtasks
  createSubtask(data: Partial<Subtask>): Observable<Subtask> {
    return this.http.post<Subtask>(`${this.api}/subtasks/`, data);
  }

  toggleSubtask(id: number): Observable<any> {
    return this.http.patch(`${this.api}/subtasks/${id}/toggle/`, {});
  }

  deleteSubtask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.api}/subtasks/${id}/`);
  }
}
