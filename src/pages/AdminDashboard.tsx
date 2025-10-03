import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useToast } from "../contexts/ToastContext";
import { User } from "../types";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import AnimatedBackground from "../components/AnimatedBackground";
import api from "../utils/api";
import { ANIMATION_VARIANTS } from "../utils/constants";

interface AdminDashboardProps {
  user: User;
}

interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: string;
  lastActive: string;
  status: "active" | "inactive";
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user }) => {
  const { success, error: showError } = useToast();
  
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRole, setSelectedRole] = useState<string>("all");
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    role: "student"
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Mock data for now - in a real implementation, this would come from API calls
      const mockUsers: AdminUser[] = [
        { id: "1", name: "Alice Johnson", email: "alice@example.com", role: "student", lastActive: "2023-05-15", status: "active" },
        { id: "2", name: "Bob Smith", email: "bob@example.com", role: "student", lastActive: "2023-05-14", status: "active" },
        { id: "3", name: "Carol Davis", email: "carol@example.com", role: "teacher", lastActive: "2023-05-16", status: "active" },
        { id: "4", name: "David Wilson", email: "david@example.com", role: "teacher", lastActive: "2023-05-12", status: "inactive" },
        { id: "5", name: "Eva Brown", email: "eva@example.com", role: "admin", lastActive: "2023-05-15", status: "active" },
        { id: "6", name: "Frank Miller", email: "frank@example.com", role: "student", lastActive: "2023-05-10", status: "active" },
      ];
      
      setUsers(mockUsers);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      showError("Error", "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    if (!newUser.name.trim() || !newUser.email.trim()) {
      showError("Error", "Please fill in all required fields");
      return;
    }
    
    try {
      // Mock API call
      const createdUser: AdminUser = {
        id: `user-${Date.now()}`,
        name: newUser.name,
        email: newUser.email,
        role: newUser.role,
        lastActive: new Date().toISOString().split('T')[0],
        status: "active"
      };
      
      setUsers(prev => [...prev, createdUser]);
      setNewUser({ name: "", email: "", role: "student" });
      setShowCreateUser(false);
      success("Success", `User "${newUser.name}" created successfully`);
    } catch (err) {
      console.error("Failed to create user:", err);
      showError("Error", "Failed to create user");
    }
  };

  const handleDeleteUser = async (userId: string, userName: string) => {
    try {
      // Mock API call
      setUsers(prev => prev.filter(user => user.id !== userId));
      success("Success", `User "${userName}" deleted successfully`);
    } catch (err) {
      console.error("Failed to delete user:", err);
      showError("Error", "Failed to delete user");
    }
  };

  const filteredUsers = users.filter(adminUser => {
    const matchesSearch = adminUser.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          adminUser.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === "all" || adminUser.role === selectedRole;
    return matchesSearch && matchesRole;
  });

  const userStats = {
    total: users.length,
    students: users.filter(u => u.role === "student").length,
    teachers: users.filter(u => u.role === "teacher").length,
    admins: users.filter(u => u.role === "admin").length,
  };

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="max-w-7xl mx-auto"
        >
          <Card className="p-8 mb-8">
            <motion.div
              variants={ANIMATION_VARIANTS.slideDown}
              className="text-center mb-8"
            >
              <h1 className="text-4xl font-bold text-purple-200 mb-2">
                Admin Dashboard
              </h1>
              <p className="text-purple-300 text-lg mb-4">
                Welcome back, {user.name || user.email}!
              </p>
            </motion.div>

            {/* Stats Cards */}
            <motion.div
              variants={ANIMATION_VARIANTS.stagger}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center mr-4">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-purple-300 text-sm">Total Users</p>
                      <p className="text-2xl font-bold text-purple-200">{userStats.total}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mr-4">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-purple-300 text-sm">Students</p>
                      <p className="text-2xl font-bold text-purple-200">{userStats.students}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center mr-4">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-purple-300 text-sm">Teachers</p>
                      <p className="text-2xl font-bold text-purple-200">{userStats.teachers}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center mr-4">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-purple-300 text-sm">Admins</p>
                      <p className="text-2xl font-bold text-purple-200">{userStats.admins}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            </motion.div>

            {/* Action Cards */}
            <motion.div
              variants={ANIMATION_VARIANTS.stagger}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">User Management</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Create, edit, and delete users. Manage roles and permissions.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={() => setShowCreateUser(true)}
                  >
                    Create User
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideRight}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">System Analytics</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    View platform usage statistics, user engagement metrics, and system performance.
                  </p>
                  <Button variant="secondary" className="w-full">
                    View Analytics
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Content Management</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Review and approve content created by teachers. Manage learning resources.
                  </p>
                  <Button variant="outline" className="w-full">
                    Manage Content
                  </Button>
                </Card>
              </motion.div>
            </motion.div>

            {/* User Management Section */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              className="mb-8"
            >
              <Card className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-4 md:mb-0">
                    User Management
                  </h2>
                  <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                    <Input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search users..."
                      className="w-full md:w-64"
                    />
                    <select
                      value={selectedRole}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="px-4 py-2 rounded-lg bg-purple-900/30 border border-purple-500/30 text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="all">All Roles</option>
                      <option value="student">Students</option>
                      <option value="teacher">Teachers</option>
                      <option value="admin">Admins</option>
                    </select>
                  </div>
                </div>

                {showCreateUser && (
                  <div className="mb-6 p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h3 className="text-lg font-semibold text-purple-200 mb-3">Create New User</h3>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                      <Input
                        type="text"
                        value={newUser.name}
                        onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                        placeholder="Full name"
                      />
                      <Input
                        type="email"
                        value={newUser.email}
                        onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                        placeholder="Email"
                      />
                      <select
                        value={newUser.role}
                        onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                        className="px-4 py-2 rounded-lg bg-purple-900/30 border border-purple-500/30 text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                        <option value="admin">Admin</option>
                      </select>
                      <div className="flex space-x-2">
                        <Button onClick={handleCreateUser} variant="primary">
                          Create
                        </Button>
                        <Button 
                          onClick={() => {
                            setShowCreateUser(false);
                            setNewUser({ name: "", email: "", role: "student" });
                          }} 
                          variant="outline"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-purple-500/30">
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">User</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Email</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Role</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Last Active</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Status</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((adminUser, index) => (
                        <motion.tr
                          key={adminUser.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="border-b border-purple-500/20 hover:bg-purple-900/10"
                        >
                          <td className="py-3 px-4 text-purple-200">{adminUser.name}</td>
                          <td className="py-3 px-4 text-purple-300">{adminUser.email}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              adminUser.role === "admin" 
                                ? "bg-red-900/30 text-red-300" 
                                : adminUser.role === "teacher" 
                                  ? "bg-blue-900/30 text-blue-300" 
                                  : "bg-green-900/30 text-green-300"
                            }`}>
                              {adminUser.role}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-purple-300">
                            {new Date(adminUser.lastActive).toLocaleDateString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              adminUser.status === "active" 
                                ? "bg-green-900/30 text-green-300" 
                                : "bg-red-900/30 text-red-300"
                            }`}>
                              {adminUser.status}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                Edit
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => handleDeleteUser(adminUser.id, adminUser.name)}
                              >
                                Delete
                              </Button>
                            </div>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {filteredUsers.length === 0 && (
                    <div className="text-center py-8 text-purple-300">
                      No users found matching your criteria.
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>
          </Card>
        </motion.div>
      </div>
    </>
  );
};

export default AdminDashboard;