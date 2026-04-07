<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Dashboard</h2>
      <div class="d-flex align-items-center">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control me-3"
          placeholder="Search students, companies, drives..."
          style="width: 350px; border-radius: 20px; padding-left: 20px;"
        />
        <button @click="logout" class="btn btn-danger">Logout</button>
      </div>
    </div>
    
    <div class="row mb-5">
      <div class="col"><div class="card border-start border-4 border-primary shadow-sm text-center py-3 bg-light"><div class="fw-bold fs-3">{{ stats.applications || 0 }}</div><div class="text-muted fw-bold small">APPLICATIONS</div></div></div>
      <div class="col"><div class="card border-start border-4 border-success shadow-sm text-center py-3 bg-light"><div class="fw-bold fs-3 text-success">{{ stats.students_selected || 0 }}</div><div class="text-muted fw-bold small">SELECTED</div></div></div>
      <div class="col"><div class="card border-start border-4 border-info shadow-sm text-center py-3 bg-light"><div class="fw-bold fs-3 text-info">{{ stats.approved_companies || 0 }}</div><div class="text-muted fw-bold small">APPROVED COMPANIES</div></div></div>
      <div class="col"><div class="card border-start border-4 border-primary shadow-sm text-center py-3 bg-light"><div class="fw-bold fs-3 text-primary">{{ stats.approved_students || 0 }}</div><div class="text-muted fw-bold small">APPROVED STUDENTS</div></div></div>
      <div class="col"><div class="card border-start border-4 border-warning shadow-sm text-center py-3 bg-light"><div class="fw-bold fs-3 text-warning">{{ stats.drives_accepted || 0 }}</div><div class="text-muted fw-bold small">ACTIVE DRIVES</div></div></div>
    </div>

    <div class="card shadow-sm mb-4 border-0" v-show="!searchQuery">
      <div class="card-header bg-warning text-dark fw-bold fs-4 py-3">
        <i class="bi-clock"></i> Pending Approvals Queue
      </div>
      <div class="card-body bg-white">
        <h5 class="fw-bold text-secondary mb-3 mt-2">Pending Student Approvals</h5>
        <table class="table table-hover align-middle mb-4" v-if="pendingStudents.length">
          <thead class="table-light"><tr><th>Student Name</th><th class="text-end">Actions</th></tr></thead>
          <tbody>
            <tr v-for="s in pendingStudents" :key="s.id">
              <td class="fw-semibold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(s, 'student')">{{ s.name }}</a></td>
              <td class="text-end">
                <button @click="approveStudent(s.id)" class="btn btn-success btn-sm me-2 rounded-pill px-3">Approve</button>
                <button @click="rejectStudent(s.id)" class="btn btn-outline-warning btn-sm me-2 rounded-pill px-3">Reject</button>
                <button @click="blacklistUser(s.user_id)" class="btn btn-dark btn-sm rounded-pill px-3">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted mb-4"><i>No students are currently waiting for approval.</i></div>

        <h5 class="fw-bold text-secondary mb-3 pt-3 border-top">Pending Company Approvals</h5>
        <table class="table table-hover align-middle mb-4" v-if="pendingCompanies.length">
          <thead class="table-light"><tr><th>Company Name</th><th>Industry</th><th class="text-end">Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in pendingCompanies" :key="c.id">
              <td class="fw-semibold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(c, 'company')">{{ c.name }}</a></td>
              <td class="text-muted">{{ c.industry }}</td>
              <td class="text-end">
                <button @click="approveCompany(c.id)" class="btn btn-success btn-sm me-2 rounded-pill px-3">Approve</button>
                <button @click="rejectCompany(c.id)" class="btn btn-outline-warning btn-sm me-2 rounded-pill px-3">Reject</button>
                <button @click="blacklistUser(c.user_id)" class="btn btn-dark btn-sm rounded-pill px-3">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted mb-4"><i>No companies are currently waiting for approval.</i></div>

        <h5 class="fw-bold text-secondary mb-3 pt-3 border-top">Pending Drive Approvals</h5>
        <table class="table table-hover align-middle" v-if="pendingJobs.length">
          <thead class="table-light"><tr><th>Drive Title</th><th>Company</th><th class="text-end">Actions</th></tr></thead>
          <tbody>
            <tr v-for="j in pendingJobs" :key="j.id">
              <td class="fw-semibold">{{ j.title }}</td>
              <td class="text-muted">{{ j.company }}</td>
              <td class="text-end">
                <button @click="approveJob(j.id)" class="btn btn-success btn-sm me-2 rounded-pill px-3">Approve</button>
                <button @click="rejectJob(j.id)" class="btn btn-outline-warning btn-sm me-2 rounded-pill px-3">Reject</button>
                <button @click="blacklistJob(j.id)" class="btn btn-dark btn-sm rounded-pill px-3">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted mb-2"><i>No job drives are currently waiting for approval.</i></div>
      </div>
    </div>

    <div v-show="!searchQuery">
      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-primary text-white fw-bold py-2">
          <i class="bi-building-check"></i> Approved Companies ({{ approvedCompanies.length }})
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="approvedCompanies.length">
            <thead class="table-light"><tr><th>Company Name</th><th>Industry</th><th>Location</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="c in approvedCompanies" :key="c.id">
                <td class="fw-bold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(c, 'company')">{{ c.name }}</a></td>
                <td>{{ c.industry }}</td>
                <td>{{ c.location }}</td>
                <td class="text-end">
                  <button @click="rejectCompany(c.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                  <button @click="blacklistUser(c.user_id)" class="btn btn-dark btn-sm">Blacklist</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No companies approved yet.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-success text-white fw-bold py-2">
          <i class="bi-person-check"></i> Approved Students ({{ approvedStudents.length }})
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="approvedStudents.length">
            <thead class="table-light"><tr><th>Student Name</th><th>Roll / Batch</th><th>Department</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="s in approvedStudents" :key="s.id">
                <td class="fw-bold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(s, 'student')">{{ s.name }}</a></td>
                <td>{{ s.roll_number }} / {{ s.batch }}</td>
                <td>{{ s.department }} ({{ s.cgpa || 'N/A' }})</td>
                <td class="text-end">
                  <button @click="rejectStudent(s.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                  <button @click="blacklistUser(s.user_id)" class="btn btn-dark btn-sm">Blacklist</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No students approved yet.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-success text-white fw-bold py-2 d-flex justify-content-between align-items-center">
          <span><i class="bi-check-circle"></i> Approved Drives ({{ approvedJobs.length }})</span>
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="approvedJobs.length">
            <thead class="table-light"><tr><th>Drive Title</th><th>Company</th><th>Spots</th><th>Applicants</th><th>Selected</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="j in approvedJobs" :key="j.id">
                <td class="fw-semibold">{{ j.title }}</td>
                <td>{{ j.company }}</td>
                <td><span class="badge bg-primary">{{ j.spots }}</span></td>
                <td><span class="badge bg-secondary">{{ j.total_applicants }}</span></td>
                <td><span class="badge bg-success">{{ j.total_selected }}</span></td>
                <td class="text-end">
                  <button @click="rejectJob(j.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                  <button @click="blacklistJob(j.id)" class="btn btn-dark btn-sm">Blacklist</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No approved drives.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-danger text-white fw-bold py-2">
          <i class="bi-x-circle"></i> Rejected / Blacklisted Drives ({{ rejectedJobs.length }})
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="rejectedJobs.length">
            <thead class="table-light"><tr><th>Drive Title</th><th>Company</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="j in rejectedJobs" :key="j.id">
                <td class="fw-semibold">{{ j.title }}</td>
                <td>{{ j.company }}</td>
                <td><span class="badge" :class="j.status === 'blacklisted' ? 'bg-dark' : 'bg-danger'">{{ j.status.toUpperCase() }}</span></td>
                <td class="text-end">
                  <button @click="approveJob(j.id)" class="btn btn-success btn-sm">Re-Approve</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No rejected or blacklisted drives.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-danger text-white fw-bold py-2">
          <i class="bi-building-dash"></i> Rejected / Blacklisted Companies ({{ rejectedCompanies.length }})
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="rejectedCompanies.length">
            <thead class="table-light"><tr><th>Company Name</th><th>Industry</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="c in rejectedCompanies" :key="c.id">
                <td class="fw-bold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(c, 'company')">{{ c.name }}</a></td>
                <td>{{ c.industry }}</td>
                <td>
                  <span class="badge" :class="c.blacklisted ? 'bg-dark' : 'bg-danger'">{{ (c.blacklisted ? 'blacklisted' : 'rejected').toUpperCase() }}</span>
                </td>
                <td class="text-end">
                  <button @click="approveCompany(c.id)" class="btn btn-success btn-sm me-2">Re-Approve</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No rejected or blacklisted companies.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0">
        <div class="card-header bg-danger text-white fw-bold py-2">
          <i class="bi-person-x"></i> Rejected / Blacklisted Students ({{ rejectedStudents.length }})
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="rejectedStudents.length">
            <thead class="table-light"><tr><th>Student Name</th><th>Roll / Batch</th><th>Status</th><th class="text-end">Actions</th></tr></thead>
            <tbody>
              <tr v-for="s in rejectedStudents" :key="s.id">
                <td class="fw-semibold"><a href="#" class="text-decoration-none" @click.prevent="viewProfile(s, 'student')">{{ s.name }}</a></td>
                <td class="text-muted small">{{ s.roll_number }} / {{ s.batch }}</td>
                <td>
                  <span class="badge" :class="s.blacklisted ? 'bg-dark' : 'bg-danger'">{{ (s.blacklisted ? 'blacklisted' : 'rejected').toUpperCase() }}</span>
                </td>
                <td class="text-end">
                  <button @click="approveStudent(s.id)" class="btn btn-success btn-sm me-2">Re-Approve</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No rejected or blacklisted students.</i></div>
        </div>
      </div>

      <div class="card shadow-sm mb-5 border-0">
        <div class="card-header bg-info text-dark fw-bold py-2 d-flex justify-content-between align-items-center">
          <span><i class="bi-people"></i> All Applicants</span>
          <select v-model="applicantStatusFilter" @change="fetchApplications" class="form-select form-select-sm" style="width: auto;">
            <option value="">All Statuses</option>
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="interview">Interview</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0" v-if="allApplications.length">
            <thead class="table-light">
              <tr><th>Student</th><th>Roll / Batch</th><th>Drive</th><th>Company</th><th>Status</th><th>View</th></tr>
            </thead>
            <tbody>
              <tr v-for="a in allApplications" :key="a.application_id">
                <td class="fw-semibold">{{ a.student_name }}</td>
                <td class="text-muted small">{{ a.student_roll }} / {{ a.student_batch }}</td>
                <td>{{ a.job_title }}</td>
                <td>{{ a.company }}</td>
                <td>
                  <span class="badge"
                    :class="{
                      'bg-warning text-dark': a.status === 'applied',
                      'bg-info text-dark': a.status === 'shortlisted' || a.status === 'interview',
                      'bg-success': a.status === 'selected',
                      'bg-danger': a.status === 'rejected'
                    }"
                  >{{ a.status.toUpperCase() }}</span>
                </td>
                <td>
                  <button @click="viewApplicantProfile(a)" class="btn btn-outline-primary btn-sm">Profile</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-muted p-3"><i>No applications found for the selected filter.</i></div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-5 border-0" v-show="searchQuery">
      <div class="card-header bg-primary text-white fw-bold fs-5 py-2">
        <i class="bi-search"></i> Search Results for "{{ searchQuery }}"
      </div>
      <div class="card-body bg-white">
        <h5 class="fw-bold mb-3">Students</h5>
        <table class="table table-sm table-bordered" v-if="filteredStudents.length">
          <thead class="table-light"><tr><th>Name</th><th>Status</th><th class="text-end w-25">Actions</th></tr></thead>
          <tbody>
            <tr v-for="s in filteredStudents" :key="s.id">
              <td><a href="#" class="text-decoration-none fw-bold" @click.prevent="viewProfile(s, 'student')">{{ s.name }}</a></td>
              <td>
                <span v-if="s.blacklisted" class="badge bg-dark">Blacklisted</span>
                <span v-else-if="s.rejected" class="badge bg-danger">Rejected</span>
                <span v-else-if="s.approved" class="badge bg-success">Approved</span>
                <span v-else class="badge bg-warning text-dark">Pending</span>
              </td>
              <td class="text-end">
                <button v-if="!s.approved" @click="approveStudent(s.id)" class="btn btn-success btn-sm me-1">Approve</button>
                <button v-if="!s.rejected" @click="rejectStudent(s.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                <button v-if="!s.blacklisted" @click="blacklistUser(s.user_id)" class="btn btn-dark btn-sm">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted small mb-4">No student records match</div>

        <h5 class="fw-bold mb-3 mt-4">Companies</h5>
        <table class="table table-sm table-bordered" v-if="filteredCompanies.length">
          <thead class="table-light"><tr><th>Name</th><th>Industry</th><th>Status</th><th class="text-end w-25">Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in filteredCompanies" :key="c.id">
              <td><a href="#" class="text-decoration-none fw-bold" @click.prevent="viewProfile(c, 'company')">{{ c.name }}</a></td>
              <td>{{ c.industry }}</td>
              <td>
                <span v-if="c.blacklisted" class="badge bg-dark">Blacklisted</span>
                <span v-else-if="c.rejected" class="badge bg-danger">Rejected</span>
                <span v-else-if="c.approved" class="badge bg-success">Approved</span>
                <span v-else class="badge bg-warning text-dark">Pending</span>
              </td>
              <td class="text-end">
                <button v-if="!c.approved" @click="approveCompany(c.id)" class="btn btn-success btn-sm me-1">Approve</button>
                <button v-if="!c.rejected" @click="rejectCompany(c.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                <button v-if="!c.blacklisted" @click="blacklistUser(c.user_id)" class="btn btn-dark btn-sm">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted small mb-4">No company records match</div>

        <h5 class="fw-bold mb-3 mt-4">All Jobs & Drives</h5>
        <table class="table table-sm table-bordered" v-if="filteredJobs.length">
          <thead class="table-light"><tr><th>Title</th><th>Company</th><th>Status</th><th class="text-end w-25">Actions</th></tr></thead>
          <tbody>
            <tr v-for="j in filteredJobs" :key="j.id">
              <td>{{ j.title }}</td>
              <td>{{ j.company }}</td>
              <td>
                <span v-if="j.status === 'blacklisted'" class="badge bg-dark">Blacklisted</span>
                <span v-else-if="j.status === 'rejected'" class="badge bg-danger">Rejected</span>
                <span v-else-if="j.status === 'approved'" class="badge bg-success">Approved</span>
                <span v-else class="badge bg-warning text-dark">{{ j.status }}</span>
              </td>
              <td class="text-end">
                <button v-if="j.status !== 'approved'" @click="approveJob(j.id)" class="btn btn-success btn-sm me-1">Approve</button>
                <button v-if="j.status !== 'rejected'" @click="rejectJob(j.id)" class="btn btn-warning btn-sm me-1">Reject</button>
                <button v-if="j.status !== 'blacklisted'" @click="blacklistJob(j.id)" class="btn btn-dark btn-sm">Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted small">No drive records match</div>
      </div>
    </div>

    <div v-if="selectedProfile" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content shadow-lg border-0">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold"><i class="bi-person-badge me-2"></i> {{ selectedProfile.name || selectedProfile.student_name }}'s Profile</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeProfile"></button>
          </div>

          <div class="modal-body p-4" v-if="profileType === 'student'">
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Full Name</div><div class="col-sm-8">{{ selectedProfile.name }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Email</div><div class="col-sm-8">{{ selectedProfile.email }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Roll / Batch</div><div class="col-sm-8">{{ selectedProfile.roll_number }} / {{ selectedProfile.batch }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Department</div><div class="col-sm-8">{{ selectedProfile.department }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Education</div><div class="col-sm-8">{{ selectedProfile.education }}</div></div>
            <div class="row mb-3 pb-3 border-bottom"><div class="col-sm-4 text-muted fw-bold">Skills</div><div class="col-sm-8">{{ selectedProfile.skills }}</div></div>
            <div class="row mb-3">
              <div class="col-12">
                <h6 class="fw-bold mb-3">Application History</h6>
                <table class="table table-sm table-hover" v-if="selectedProfile.applications && selectedProfile.applications.length">
                  <thead class="table-light"><tr><th>Job Drive</th><th>Company</th><th>Status</th></tr></thead>
                  <tbody>
                    <tr v-for="(a, i) in selectedProfile.applications" :key="i">
                      <td class="fw-semibold">{{ a.job }}</td>
                      <td>{{ a.company }}</td>
                      <td><span class="badge bg-secondary">{{ a.status.toUpperCase() }}</span></td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="text-muted small"><i>No applications recorded.</i></div>
              </div>
            </div>
          </div>

          <div class="modal-body p-4" v-else-if="profileType === 'applicant'">
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Full Name</div><div class="col-sm-8">{{ selectedProfile.student_name }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Email</div><div class="col-sm-8">{{ selectedProfile.student_email }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Roll / Batch</div><div class="col-sm-8">{{ selectedProfile.student_roll }} / {{ selectedProfile.student_batch }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Department</div><div class="col-sm-8">{{ selectedProfile.student_department }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Education</div><div class="col-sm-8">{{ selectedProfile.student_education }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Skills</div><div class="col-sm-8">{{ selectedProfile.student_skills }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Applied Drive</div><div class="col-sm-8 fw-bold">{{ selectedProfile.job_title }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Company</div><div class="col-sm-8">{{ selectedProfile.company }}</div></div>
            <div class="row mb-3"><div class="col-sm-4 text-muted fw-bold">Resume</div><div class="col-sm-8"><a v-if="selectedProfile.student_resume" :href="selectedProfile.student_resume" target="_blank">View PDF</a><span v-else>Not uploaded</span></div></div>
          </div>

          <!-- Company Profile -->
          <div class="modal-body p-4" v-else-if="profileType === 'company'">
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Company Name</div><div class="col-sm-8">{{ selectedProfile.name }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Contact Email</div><div class="col-sm-8">{{ selectedProfile.email }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Industry</div><div class="col-sm-8">{{ selectedProfile.industry }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Location</div><div class="col-sm-8">{{ selectedProfile.location }}</div></div>
            <div class="row mb-3 border-bottom pb-2"><div class="col-sm-4 text-muted fw-bold">Website</div><div class="col-sm-8"><a v-if="selectedProfile.website !== 'Not provided'" :href="selectedProfile.website" target="_blank">{{ selectedProfile.website }}</a><span v-else>{{ selectedProfile.website }}</span></div></div>
            <div class="row mb-3"><div class="col-sm-4 text-muted fw-bold">Description</div><div class="col-sm-8">{{ selectedProfile.description }}</div></div>
          </div>

          <div class="modal-footer bg-light">
            <div class="me-auto" v-if="profileType !== 'applicant'">
              <span v-if="selectedProfile.blacklisted" class="badge bg-dark fs-6">Status: Blacklisted</span>
              <span v-else-if="selectedProfile.rejected" class="badge bg-danger fs-6">Status: Rejected</span>
              <span v-else-if="selectedProfile.approved" class="badge bg-success fs-6">Status: Approved</span>
              <span v-else-if="selectedProfile.status" class="badge bg-secondary fs-6">Application: {{ selectedProfile.status }}</span>
              <span v-else class="badge bg-warning text-dark fs-6">Status: Pending</span>
            </div>
            <div class="me-auto" v-else>
              <span class="badge fs-6"
                :class="{
                  'bg-warning text-dark': selectedProfile.status === 'applied',
                  'bg-info text-dark': selectedProfile.status === 'shortlisted' || selectedProfile.status === 'interview',
                  'bg-success': selectedProfile.status === 'selected',
                  'bg-danger': selectedProfile.status === 'rejected'
                }"
              >Application Status: {{ selectedProfile.status?.toUpperCase() }}</span>
            </div>
            <button type="button" class="btn btn-secondary px-4" @click="closeProfile">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      searchQuery: '',
      stats: {},
      companies: [],
      students: [],
      jobs: [],
      allApplications: [],
      applicantStatusFilter: '',
      selectedProfile: null,
      profileType: ''
    }
  },
  computed: {
    filteredCompanies() {
      const q = this.searchQuery.toLowerCase()
      if (!q) return this.companies
      return this.companies.filter(c =>
        (c.name && c.name.toLowerCase().includes(q)) ||
        (c.industry && c.industry.toLowerCase().includes(q))
      )
    },
    filteredStudents() {
      const q = this.searchQuery.toLowerCase()
      if (!q) return this.students
      return this.students.filter(s => s.name && s.name.toLowerCase().includes(q))
    },
    filteredJobs() {
      const q = this.searchQuery.toLowerCase()
      if (!q) return this.jobs
      return this.jobs.filter(j =>
        (j.title && j.title.toLowerCase().includes(q)) ||
        (j.company && j.company.toLowerCase().includes(q))
      )
    },
    pendingCompanies() {
      return this.companies.filter(c => !c.approved && !c.rejected && !c.blacklisted)
    },
    pendingStudents() {
      return this.students.filter(s => !s.approved && !s.rejected && !s.blacklisted)
    },
    pendingJobs() {
      return this.jobs.filter(j => j.status === 'pending')
    },
    approvedJobs() {
      return this.jobs.filter(j => j.status === 'approved')
    },
    approvedCompanies() {
      return this.companies.filter(c => c.approved && !c.blacklisted)
    },
    approvedStudents() {
      return this.students.filter(s => s.approved && !s.blacklisted)
    },
    rejectedJobs() {
      return this.jobs.filter(j => j.status === 'rejected' || j.status === 'blacklisted')
    },
    rejectedStudents() {
      return this.students.filter(s => s.rejected || s.blacklisted)
    },
    rejectedCompanies() {
      return this.companies.filter(c => c.approved === false && (c.rejected || c.blacklisted))
    }
  },
  async mounted() {
    this.fetchData()
    this.fetchApplications()
  },
  methods: {
    viewProfile(entity, type) {
      this.selectedProfile = entity
      this.profileType = type
    },
    viewApplicantProfile(app) {
      this.selectedProfile = app
      this.profileType = 'applicant'
    },
    closeProfile() {
      this.selectedProfile = null
      this.profileType = ''
    },
    async fetchData() {
      try {
        const stats = await axios.get('http://127.0.0.1:5000/api/admin/dashboard', { withCredentials: true })
        this.stats = stats.data
        const companies = await axios.get('http://127.0.0.1:5000/api/admin/companies', { withCredentials: true })
        this.companies = companies.data
        const students = await axios.get('http://127.0.0.1:5000/api/admin/students', { withCredentials: true })
        this.students = students.data
        const jobs = await axios.get('http://127.0.0.1:5000/api/admin/jobs', { withCredentials: true })
        this.jobs = jobs.data
      } catch (error) {
        console.error('Failed to fetch admin data.', error)
        if (error.response && error.response.status === 401) this.$router.push('/')
      }
    },
    async fetchApplications() {
      try {
        const url = this.applicantStatusFilter
          ? `http://127.0.0.1:5000/api/admin/all_applications?status=${this.applicantStatusFilter}`
          : 'http://127.0.0.1:5000/api/admin/all_applications'
        const res = await axios.get(url, { withCredentials: true })
        this.allApplications = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async approveCompany(id) { await axios.post(`http://127.0.0.1:5000/api/admin/approve_company/${id}`, {}, { withCredentials: true }); this.fetchData(); this.closeProfile() },
    async rejectCompany(id) { await axios.post(`http://127.0.0.1:5000/api/admin/reject_company/${id}`, {}, { withCredentials: true }); this.fetchData(); this.closeProfile() },
    async approveStudent(id) { await axios.post(`http://127.0.0.1:5000/api/admin/approve_student/${id}`, {}, { withCredentials: true }); this.fetchData(); this.closeProfile() },
    async rejectStudent(id) { await axios.post(`http://127.0.0.1:5000/api/admin/reject_student/${id}`, {}, { withCredentials: true }); this.fetchData(); this.closeProfile() },
    async blacklistUser(userId) { await axios.post(`http://127.0.0.1:5000/api/admin/blacklist_user/${userId}`, {}, { withCredentials: true }); this.fetchData(); this.closeProfile() },
    async approveJob(id) { await axios.post(`http://127.0.0.1:5000/api/admin/approve_job/${id}`, {}, { withCredentials: true }); this.fetchData() },
    async rejectJob(id) { await axios.post(`http://127.0.0.1:5000/api/admin/reject_job/${id}`, {}, { withCredentials: true }); this.fetchData() },
    async blacklistJob(id) { await axios.post(`http://127.0.0.1:5000/api/admin/blacklist_job/${id}`, {}, { withCredentials: true }); this.fetchData() },
    async logout() {
      try { await axios.get('http://127.0.0.1:5000/api/logout', { withCredentials: true }) } catch (e) { console.error(e) } finally { this.$router.push('/') }
    }
  }
}
</script>
