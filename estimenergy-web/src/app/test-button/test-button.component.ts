import { Component } from '@angular/core';
import { NgbCollapseModule } from '@ng-bootstrap/ng-bootstrap';
import { DefaultService } from '../api';

@Component({
  selector: 'app-test-button',
  templateUrl: './test-button.component.html',
  styleUrls: ['./test-button.component.css'],
})
export class TestButtonComponent {
  public isCollapsed: boolean = false;
  private defaultService: DefaultService;

  constructor(defaultService: DefaultService) {
    this.defaultService = defaultService;
  }

  onClick() {
    console.log("Test");

    this.defaultService.getDaysDayGet().subscribe(
      (data) => {
        console.log(data);
      }
    );
  }
}
