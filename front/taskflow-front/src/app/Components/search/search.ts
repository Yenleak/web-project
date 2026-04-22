import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TaskService } from '../../Services/task';
import { Task } from '../../Models/task';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search.html',
  styleUrl: './search.css'
})
export class Search {
  query = '';
  results: Task[] = [];
  allTasks: Task[] = [];
  searched = false;
  error = '';

  constructor(private taskService: TaskService, private router: Router) {}

  loadAndSearch() {
    if (!this.query.trim()) return;
    if (this.allTasks.length === 0) {
      this.taskService.getTasks().subscribe({
        next: (data) => {
          this.allTasks = data;
          this.filterResults();
        },
        error: () => this.error = 'Ошибка загрузки задач'
      });
    } else {
      this.filterResults();
    }
  }

  filterResults() {
    const q = this.query.toLowerCase();
    this.results = this.allTasks.filter(t =>
      t.title.toLowerCase().includes(q) ||
      t.description.toLowerCase().includes(q)
    );
    this.searched = true;
  }

  openTask(id: number) {
    this.router.navigate(['/tasks', id]);
  }

  isOverdue(task: Task): boolean {
    if (!task.deadline || task.is_completed) return false;
    return new Date(task.deadline) < new Date();
  }
}
