import { User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function MemberSelector() {
  const { members, selectedMember, setSelectedMember } = useAuth();

  if (members.length === 0) {
    return (
      <div className="flex items-center gap-2 text-gray-500">
        <User className="w-5 h-5" />
        <span>Loading members...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <label htmlFor="member-select" className="sr-only">
        Select member
      </label>
      <select
        id="member-select"
        value={selectedMember?.id || ''}
        onChange={(e) => {
          const member = members.find(m => m.id === e.target.value);
          setSelectedMember(member);
        }}
        className="appearance-none w-full md:w-64 px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent cursor-pointer"
      >
        <option value="">Select a member...</option>
        {members.map((member) => (
          <option key={member.id} value={member.id}>
            {member.full_name} ({member.username})
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
        <User className="w-5 h-5" />
      </div>
    </div>
  );
}