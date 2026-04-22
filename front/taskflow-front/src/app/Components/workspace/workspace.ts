import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WorkspaceService } from '../../Services/workspace';
import { Workspace } from '../../Models/workspace';

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './workspace.html',
  styleUrl: './workspace.css'
})
export class WorkspaceComponent implements OnInit {
  workspaces: Workspace[] = [];
  error = '';
  showForm = false;

  newWorkspace = {
    name: '',
    deadline: ''
  };

  constructor(private workspaceService: WorkspaceService, private router: Router) {}

  ngOnInit() {
    this.loadWorkspaces();
  }

  loadWorkspaces() {
    this.workspaceService.getWorkspaces().subscribe({
      next: (data) => this.workspaces = data,
      error: () => this.error = 'Ошибка загрузки воркспейсов'
    });
  }

  createWorkspace() {
    if (!this.newWorkspace.name.trim()) return;
    this.workspaceService.createWorkspace(this.newWorkspace).subscribe({
      next: (ws) => {
        this.workspaces.unshift(ws);
        this.showForm = false;
        this.newWorkspace = { name: '', deadline: '' };
      },
      error: () => this.error = 'Ошибка создания воркспейса'
    });
  }

  openWorkspace(id: number) {
    this.router.navigate(['/workspaces', id]);
  }

  isOverdue(deadline: string | null): boolean {
    if (!deadline) return false;
    return new Date(deadline) < new Date();
  }
}
