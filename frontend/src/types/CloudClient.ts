export interface CloudClient {
  id: string;
  name: string;
  description: string;
  providers: string[];
  iam_role_arn?: string;
  created_at: string;
  updated_at: string;
}